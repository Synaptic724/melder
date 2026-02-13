import threading
from collections import deque
from typing import Deque, Optional

from melder.utilities.general_base.cleanable import Cleanable


class CounterSwitch(Cleanable):
    """
    Deque-backed counter latch with event-gated selector wait behavior.

    Purpose:
        Provide a low-overhead primitive where deque ticket cardinality is the
        state value and an event controls when blocked selector callers are
        released.

    Counter model:
        - ``0``: idle; no owner, no completion.
        - ``1``: pending; one owner is building.
        - ``>=2``: complete/open latch; all entrants pass fast.

    Selector contract:
        - ``selector()`` returns immediately when state is already open
          (``>=2``).
        - For state below open threshold (``0`` or ``1``), selector waits on
          the internal event.
        - Once the event is signalled, selector returns current ticket count.
        - Selector timeout raises ``TimeoutError``.

    Ownership model:
        - Ticket mutation is explicit and externalized.
        - ``push_ticket()`` is owned by the leader path and intentionally does
          not perform wake signalling by itself.

    Design intent:
        - This primitive is intentionally non-defensive for speed.
        - It does not call ``check_cleaned()``.
        - It does not guard cleanup idempotence.
    """

    __slots__ = ("_event", "_tickets")

    def __init__(self, state: int = 2) -> None:
        """
        Public API

        Initialize counter state from a starting ticket count.

        Args:
            state:
                Initial ticket count encoded into deque cardinality. The
                default ``2`` starts this switch in open-latch mode.
                Event state mapping at construction:
                - ``state == 1``: event is cleared (pending gate).
                - otherwise: event is set (open gate).

        Returns:
            None.
        """
        super().__init__()
        self._event: Optional[threading.Event] = threading.Event()
        self._tickets: Optional[Deque[None]] = deque()
        if state > 0:
            self._tickets.extend([None] * state)
        if state == 1:
            self._event.clear()
        else:
            self._event.set()

    def cleanup(self) -> None:
        """
        Public API

        Wake waiters and break this primitive.

        Purpose:
            Release currently waiting selector callers, then invalidate this
            primitive.

        Contract:
            - Clears all tickets.
            - Sets event so current waiters can leave ``Event.wait()``.
            - Marks cleaned and nulls event reference.
            - No guard checks are performed.

        Returns:
            None.
        """
        self._tickets.clear()
        self._event.set()
        self._cleaned = True
        self._event = None

    def __len__(self) -> int:
        """
        Public API

        Return current ticket count.

        Returns:
            int:
                Current deque cardinality.
        """
        return len(self._tickets)

    def __bool__(self) -> bool:
        """
        Public API

        Return True when counter has reached complete/open threshold.

        Returns:
            bool:
                True when ticket count is two or greater.
        """
        return self.state >= 2

    @property
    def state(self) -> int:
        """
        Public API

        Expose current counter value derived from ticket count.

        Returns:
            int:
                Current ticket count.
        """
        return len(self._tickets)

    def reset(self) -> None:
        """
        Public API

        Reset this primitive to idle-and-blocking state.

        Contract:
            - Clears all tickets (state becomes ``0``).
            - Clears event so selector callers block until signalled.

        Returns:
            None.
        """
        self._tickets.clear()
        self._event.clear()

    def push_ticket(self) -> None:
        """
        Public API

        Append one leader-owned ticket.

        Contract:
            - Appends one ticket to the deque.
            - Performs no event signalling.
            - Does not guard against overflow or ownership misuse.
            - Intended to be called by the leader path only.

        Returns:
            None.
        """
        self._tickets.append(None)


    def selector(self, timeout_seconds: float | None = None) -> int:
        """
        Public API

        Enter selector admission and return current state.

        Contract:
            - Fast path:
                - Returns immediately when state is already open ``>=2``.
            - Wait path:
                - For state ``0`` or ``1``, waits on the internal event.
            - Returns actual state value after admission/wait logic.

        Args:
            timeout_seconds:
                Optional timeout passed directly to ``Event.wait``.

        Returns:
            int:
                Current state after selector admission:
                ``0`` idle, ``1`` leader-claimed pending, ``>=2`` open latch.

        Raises:
            TimeoutError:
                If timeout expires before the event is signalled.
        """
        count = len(self._tickets)
        if count >= 2:
            return count

        completed = self._event.wait(timeout=timeout_seconds)
        if not completed:
            raise TimeoutError(
                "CounterSwitch selector timed out while pending."
            )
        return len(self._tickets)
