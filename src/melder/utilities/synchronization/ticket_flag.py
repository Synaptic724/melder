from collections import deque
from typing import Deque, Literal, Optional

from mypy_extensions import mypyc_attr
from melder.utilities.general_base.cleanable import Cleanable

@mypyc_attr(native_class=True)
class TicketFlag(Cleanable):
    """
    Deque-backed boolean-style flag using ticket cardinality.

    Purpose:
        Provide a low-overhead truthy/falsey primitive where truth value is
        derived from ticket count instead of a dedicated boolean field.

    Truth model:
        - "True" means at least one active ticket exists.
        - "False" means no active tickets exist.
        - Setting "value=True" appends one "None" ticket.
        - Setting "value=False" removes one ticket when available.

    Threading:
        - This primitive does not use an explicit Python lock.
        - It relies on the runtime's deque operation safety for individual
          append/pop/len operations.
        - Multi-step workflows across multiple method calls are not atomic as
          a single transaction.
    """

    __slots__ = ("_tickets",)

    def __init__(self, value: bool = False) -> None:
        """
        Public API

        Initialize the flag in a truthy or falsey state.

        Purpose:
            Create a ticket-backed flag that can be used in "if" statements
            while preserving ticket-count introspection.

        Contract:
            - "value=False" starts with zero tickets.
            - "value=True" starts with one ticket.
            - Additional truthy writes may increase the ticket count beyond one.

        Args:
            value:
                Initial truth value for this flag.

        Returns:
            None.
        """
        super().__init__()
        self._tickets: Deque[None] = deque()
        if value:
            self._tickets.append(None)

    def cleanup(self) -> None:
        """
        Public API

        Idempotently clear all tickets and invalidate the flag.

        Purpose:
            Release owned ticket storage and mark the flag unusable for future
            operations.

        Contract:
            - Cleanup is idempotent.
            - All tickets are cleared before invalidation.
            - All guarded operations rise after cleanup.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._tickets.clear()
        self._cleaned = True
        self._tickets = None

    def __bool__(self) -> bool:
        """
        Public API

        Return the current truth value derived from ticket count.

        Returns:
            bool:
                True when at least one ticket exists; otherwise False.

        Raises:
            RuntimeError:
                If called after cleanup().
        """
        self.check_cleaned()
        return len(self._tickets) > 0

    def __len__(self) -> int:
        """
        Public API

        Return active ticket count.

        Returns:
            int:
                Number of active tickets.

        Raises:
            RuntimeError:
                If called after cleanup().
        """
        self.check_cleaned()
        return len(self._tickets)

    @property
    def value(self) -> bool:
        """
        Public API

        Return a boolean view of the current ticket state.

        Returns:
            bool:
                True when at least one ticket exists; otherwise False.

        Raises:
            RuntimeError:
                If accessed after cleanup().
        """
        return bool(self)

    @value.setter
    def value(self, new_value: bool) -> None:
        """
        Public API

        Update the flag using ticket operations.

        Contract:
            - new_value=True appends one ticket.
            - new_value=False removes one ticket when available.
            - Empty-pop is treated as a no-op.

        Args:
            new_value:
                Target truth value operation.

        Returns:
            None.

        Raises:
            RuntimeError:
                If set after cleanup().
        """
        self.check_cleaned()
        if new_value:
            self._tickets.append(None)
            return
        try:
            self._tickets.pop()
        except IndexError:
            pass

    def set_true(self) -> None:
        """
        Public API

        Append one ticket to make/keep the flag truthy.

        Returns:
            None.

        Raises:
            RuntimeError:
                If set after cleanup().
        """
        self.check_cleaned()
        self.value = True

    def set_false(self) -> None:
        """
        Public API

        Remove one ticket to move the flag toward falsey state.

        Contract:
            - Removes at most one ticket.
            - Empty state remains unchanged.

        Returns:
            None.

        Raises:
            RuntimeError:
                If called after cleanup().
        """
        self.check_cleaned()
        self.value = False

    def clear_tickets(self) -> None:
        """
        Public API

        Remove all tickets and force falsey state.

        Returns:
            None.

        Raises:
            RuntimeError:
                If called after cleanup().
        """
        self.check_cleaned()
        self._tickets.clear()

    def has_tickets(self) -> bool:
        """
        Public API

        Return whether at least one active ticket exists.

        This is a thin alias over: meth:`__bool__`.

        Returns:
            True when at least one ticket exists.

        Raises:
            RuntimeError:
                If called after cleanup().
        """
        return bool(self)

    def active_ticket_count(self) -> int:
        """
        Public API

        Return the number of active tickets.

        This is a thin alias over: meth:`__len__`.

        Returns:
            Active ticket count.

        Raises:
            RuntimeError:
                If called after cleanup().
        """
        return len(self)

    def __enter__(self) -> "TicketFlag":
        """
        Public API

        Context-enter by appending one ticket.

        Returns:
            This flag instance after one truthy increment.

        Raises:
            RuntimeError:
                If entered after cleanup().
        """
        self.set_true()
        return self

    def __exit__(self, exc_type, exc, tb) -> bool | Literal[False]:
        """
        Public API

        Context-exit by removing one ticket.

        Contract:
            - Always attempts one decrement.
            - Never suppresses exceptions from the with-body.

        Returns:
            False.

        Raises:
            RuntimeError:
                If exited after cleanup().
        """
        self.set_false()
        return False
