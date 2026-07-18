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

    Design intent:
        - Minimal API surface for hot paths.
        - Non-defensive by design.

    Lifecycle:
        - "cleanup()" terminally opens and idles the switch: tickets clear to
          the terminal "0" state and the event is set so parked selectors are
          released. All four slots are RETAINED ALIVE as documented terminal
          surfaces (LoadGate tombstone law; not del): a parked selector may
          still be inside "selector()" when cleanup runs, wakes on the event,
          re-checks cleaned state, and exits with the terminal "0". Deleting
          the slots (normal del posture) would raise AttributeError inside
          that waiter, so "_event" stays alive terminally set as the
          terminal-open surface, "_tickets" stays alive empty, and
          "_lock"/"fast_state" stay alive for in-flight leader claims and
          hot readers.
    """

    __slots__ = ("_lock", "_event", "_tickets", "fast_state")
    def __init__(self, state: int = 2) -> None:
        """
        Public API

        Initialize counter state from ticket cardinality.

        Args:
            state:
                Initial ticket count. Default "2" starts open.
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

        Tear down this primitive and release any waiting selectors.

        Contract:
            - Idempotent; safe under concurrent double-cleanup.
            - Clears all tickets and the fast-state mirror to the terminal
              "0" state, then sets the event so parked followers are released
              into that terminal state.
            - RETAINED TERMINAL SURFACES (LoadGate tombstone law; not del):
              a parked follower may still be inside "selector()" when cleanup
              runs; it wakes on the event, re-checks cleaned state, and exits
              with the terminal "0". Deleting the slots (normal del posture)
              would raise AttributeError inside that waiter, so all four
              slots stay alive: "_event" terminally set as the terminal-open
              surface, "_tickets" alive and empty, "_lock" alive for
              in-flight leader claims, "fast_state" zeroed for hot readers.

        Threading:
            - Teardown serializes with "selector()" leader claims on the
              existing claim lock so a racing claim can never clear the
              terminally set event after cleanup. Hot paths ("advance",
              the ">=2" selector fast path) remain lockless and untouched.
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

        Return the current raw ticket count.
        """
        return len(self._tickets)

    def __bool__(self) -> bool:
        """
        Public API

        Return whether the switch is currently open (`state >= 2`).
        """
        return len(self._tickets) >= 2

    @property
    def state(self) -> int:
        """
        Public API

        Return the raw deque-backed state value.
        """
        return len(self._tickets)

    def advance(self, delta: int) -> int:
        """
        Public API

        Apply signed state delta.

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
                if self._cleaned:
                    # Terminal posture: cleanup already idled the switch.
                    # Claiming here would clear the terminally set event
                    # and park later followers forever.
                    return 0
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
        if self._cleaned:
            # Woken (or passed) by cleanup: re-check per the retained
            # terminal-surface contract and exit with the terminal state
            # instead of re-reading live-path state.
            return 0
        return len(self._tickets)
