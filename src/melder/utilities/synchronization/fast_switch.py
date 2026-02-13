from collections import deque
from typing import Deque, Optional

from melder.utilities.general_base.cleanable import Cleanable


class FastSwitch(Cleanable):
    """
    Ultra-light ticket-backed boolean switch for hot paths.

    Purpose:
        Provide the cheapest possible bool-like and counter-like primitive
        backed by deque ticket operations.

    State model:
        - Truth value is derived from ticket count.
        - ``True`` means at least one active ticket exists.
        - ``False`` means ticket count is zero.
        - ``set_true`` appends one ticket.
        - ``set_false`` pops one ticket.

    Design intent:
        - This primitive is intentionally non-defensive.
        - It does not call ``check_cleaned()``.
        - It does not guard underflow in ``set_false``.
        - It is a "shoot your foot" primitive intended for controlled,
          performance-critical call sites.

    Threading:
        - No explicit Python lock is used.
        - Uses deque operations as the synchronization boundary for this
          primitive's hot-path mechanics.
    """

    __slots__ = ("_tickets",)

    def __init__(self, value: bool = False) -> None:
        """
        Public API

        Initialize the switch with optional truthy state.

        Args:
            value:
                When True, starts with one ticket (truthy).
                When False, starts empty (falsey).

        Returns:
            None.
        """
        super().__init__()
        self._tickets: Optional[Deque[None]] = deque()
        if value:
            self._tickets.append(None)

    def cleanup(self) -> None:
        """
        Public API

        Release deque resources and break this primitive.

        Purpose:
            Explicitly tear down ticket storage for deterministic teardown in
            systems that aggressively clean runtime primitives.

        Contract:
            - Clears all tickets.
            - Marks this primitive cleaned.
            - Nulls internal ticket storage.
            - No cleanup guard or idempotence check is applied.

        Returns:
            None.
        """
        self._tickets.clear()
        self._cleaned = True
        self._tickets = None

    def __bool__(self) -> bool:
        """
        Public API

        Return switch truth value based on ticket presence.

        Returns:
            bool:
                True when at least one ticket exists.
        """
        return len(self._tickets) > 0

    def __len__(self) -> int:
        """
        Public API

        Return current ticket count.

        Returns:
            int:
                Number of active tickets.
        """
        return len(self._tickets)

    @property
    def value(self) -> bool:
        """
        Public API

        Boolean view over current ticket count.

        Returns:
            bool:
                True when at least one ticket exists.
        """
        return bool(self)

    @value.setter
    def value(self, new_value: bool) -> None:
        """
        Public API

        Set switch state via ticket operations.

        Contract:
            - ``True`` appends one ticket.
            - ``False`` pops one ticket.
            - Underflow is not guarded.

        Args:
            new_value:
                Target truth operation.

        Returns:
            None.
        """
        if new_value:
            self.set_true()
            return
        self.set_false()

    def set_true(self) -> None:
        """
        Public API

        Append one ticket to make/keep switch truthy.

        Returns:
            None.
        """
        self._tickets.append(None)

    def set_false(self) -> None:
        """
        Public API

        Pop one ticket to move switch toward falsey state.

        Contract:
            - No underflow guard.
            - Empty-pop raises IndexError.

        Returns:
            None.
        """
        self._tickets.pop()

    def clear_tickets(self) -> None:
        """
        Public API

        Remove all tickets and force falsey state.

        Returns:
            None.
        """
        self._tickets.clear()
