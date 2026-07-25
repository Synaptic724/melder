from collections import deque
from types import TracebackType
from typing import Deque, Literal, Optional, ClassVar


from melder.utilities.general_base.cleanable import Cleanable


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

    Responsibilities:
        - Hold a truthy/falsey value derived from ticket cardinality.
        - Support nested scoping through the context-manager protocol.
        - Guard every operation against use after cleanup.

    IT IS A DEPTH COUNTER, NOT A BOOLEAN:
        Truth is `count > 0`, and truthy writes STACK. Three `set_true()` calls
        need three `set_false()` calls to go falsey again. That is what makes
        the context-manager form meaningful: nested `with flag:` blocks track
        how many regions are currently active, and the flag stays truthy until
        the outermost one exits.

            with flag:          # count 1 - truthy
                with flag:      # count 2 - still truthy
                    ...
                                # count 1 - STILL truthy, inner exit only
                                # count 0 - now falsey

        Use it to answer "is anything currently inside this region", not "is
        this thing on".

    Contract:
        - Empty-pop is a NO-OP. `set_false()` on an already-falsey flag leaves
          it falsey rather than raising, so unbalanced exits degrade quietly.
        - `__exit__` never suppresses exceptions from the with-body.
        - `has_tickets()` and `active_ticket_count()` are thin aliases over
          `__bool__` and `__len__`.

    Cleaned-State Guarding:
        Uniform, unlike its `FastSwitch` sibling. Every public operation guards:
        `__bool__`, `__len__`, the `value` setter, `set_true`, `set_false`, and
        `clear_tickets` call `check_cleaned()` directly; the `value` getter,
        `has_tickets()`, `active_ticket_count()`, `__enter__`, and `__exit__`
        guard transitively through the methods they delegate to.

    Owned State:
        - `_tickets`: a deque whose LENGTH is the entire state. Elements are
          `None`; only the count carries meaning.

    Threading:
        - This primitive does not use an explicit Python lock.
        - It relies on the runtime's deque operation safety for individual
          append/pop/len operations.
        - Multi-step workflows across multiple method calls are not atomic as
          a single transaction.
        - LIMIT OF THAT GUARANTEE: individual `append`/`pop` are atomic, so the
          COUNT is safe under concurrency. A read-then-act sequence is not -
          `if flag: ...` can be invalidated between the test and the body. Use
          the context-manager form when the region itself must be tracked.

    Lifecycle / Cleanup:
        - Idempotent: guarded on `_cleaned`, so a second call is a no-op.
        - Clears tickets, marks cleaned, then releases `_tickets` under normal
          del posture. Post-cleanup use raises, which is the intended loud
          failure for out-of-contract use.

    Registration:
        Exported for direct use as your own flag (owner ruling 2026-07-19).

    Subsystem Context:
        Part of the switch family in `utilities/synchronization/`, and the SAFE
        counterpart to `FastSwitch`. Same deque-cardinality idea, opposite
        trade-offs at every point:

            FastSwitch  - `__bool__` unguarded, empty-pop RAISES IndexError,
                          cleanup NOT idempotent, no context manager.
            TicketFlag  - every op guarded, empty-pop is a no-op, cleanup IS
                          idempotent, usable as a context manager.

        Reach for `FastSwitch` only on a proven hot path where you own the
        invariant; reach for this one by default. `CounterSwitch` is the third
        member and answers a different question entirely - it elects a leader
        and parks followers rather than counting depth.

    System Context:
        A substrate primitive with no position in the DGR boot order. Its
        context-manager shape is the reason it exists: regions of runtime work
        that need to know whether anyone is currently inside them can wrap
        entry and exit without hand-maintaining a counter and without paying
        for a lock.
    """

    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. Depth-counting flag: truthy while at least one ticket "
        "is held, and truthy writes STACK. Use `with flag:` to track whether "
        "anything is currently inside a region. Safe sibling of FastSwitch - "
        "every op is guarded and empty-pop is a no-op rather than an error."
    )

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
        del self._tickets

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

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> Literal[False]:
        """
        Public API

        Context-exit by removing one ticket.

        Contract:
            - Always attempts one decrement.
            - Never suppresses exceptions from the with-body.

        Args:
            exc_type:
                Exception type raised in the with-body, or None.
            exc:
                Exception instance raised in the with-body, or None.
            tb:
                Traceback for the with-body exception, or None.

        Returns:
            False.

        Raises:
            RuntimeError:
                If exited after cleanup().
        """
        self.set_false()
        return False
