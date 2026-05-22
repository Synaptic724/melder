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

    Design intent:
        - Minimal API surface for hot paths.
        - Non-defensive by design.
    """

    __slots__ = ("_lock", "_event", "_tickets")
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
        if state == 1:
            self._event.clear()
        else:
            self._event.set()

    def cleanup(self) -> None:
        """
        Public API

        Tear down this primitive and release any waiting selectors.

        Contract:
            - Clears all tickets before invalidation.
            - Sets the event before nulling references so waiting followers are
              released.
            - Marks the switch cleaned and drops lock/event/ticket storage.
        """
        if self._cleaned:
            return

        self._tickets.clear()
        self._event.set()
        self._cleaned = True

        del self._event
        del self._tickets
        del self._lock

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
        self.check_cleaned()
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
        self.check_cleaned()
        if delta == 0:
            return len(self._tickets)
        if delta > 0:
            self._tickets.extend([None] * delta)
        else:
            for _ in range(-delta):
                self._tickets.pop()
        count = len(self._tickets)
        if count == 1:
            self._event.clear()
        else:
            self._event.set()
        return count

    def selector(self, timeout_seconds: float | None = None) -> int:
        """
        Public API

        Enter a selector and return the current state.

        Args:
            timeout_seconds:
                Optional follower wait timeout.

        Returns:
            int:
                Current state after leader election or follower wake-up.

        Raises:
            TimeoutError:
                If a follower waits at pending state, and the event is not
                signalled before `timeout_seconds` expires.
        """
        self.check_cleaned()
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
                    self._event.clear()
                    return 1

        completed = self._event.wait(timeout=timeout_seconds)
        if not completed:
            raise TimeoutError(
                "CounterSwitch selector timed out while pending."
            )
        return len(self._tickets)
