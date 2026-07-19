from collections import deque
from typing import Deque, ClassVar

from melder.utilities.general_base.cleanable import Cleanable




class FastSwitch(Cleanable):
    """
    Ultra-light ticket-backed boolean switch for hot paths.

    Purpose:
        Provide the cheapest possible bool-like and counter-like primitive
        backed by deque ticket operations.

    State model:
        - Truth value is derived from ticket count.
        - "True" means at least one active ticket exists.
        - "False" means ticket count is zero.
        - "set_true" appends one ticket.
        - "set_false" pops one ticket.

    Design intent:
        - This primitive is intentionally non-defensive.
        - It does not guard underflow in "set_false".
        - It is a "shoot your foot" primitive intended for controlled,
          performance-critical call sites.

    Cleaned-State Guarding (read this - it is NOT uniform):
        - Guards DIRECTLY: `__len__()`, the `value` getter, `set_true()`,
          `set_false()`, `clear_tickets()`.
        - Guards TRANSITIVELY: the `value` setter, which holds no guard of its
          own but delegates to `set_true()` / `set_false()`.
        - Genuinely UNGUARDED: `__bool__()`, the hot read.

        On a CLEANED switch, `bool(...)` raises `AttributeError` because
        `cleanup()` deletes `_tickets`. That is correct, not a defect: the
        repository law is that a cleaned object is not used again, so a dead
        switch failing loudly beats it quietly answering False and letting a
        use-after-clean pass unnoticed.

    Underflow:
        `set_false()` pops without checking. On an empty switch it raises
        `IndexError`. That is deliberate - the primitive trades safety for speed
        and expects the call site to own the invariant.

    Threading:
        - No explicit Python lock is used.
        - Uses deque operations as the synchronization boundary for this
          primitive's hot-path mechanics.
        - LIMIT OF THAT GUARANTEE: individual `deque.append` / `deque.pop` calls
          are atomic, so the COUNT is safe under concurrency. The switch
          SEMANTICS are not. Two threads calling `set_false()` on a one-ticket
          switch can both pass their guard; one pops and the other raises
          `IndexError`. Treat this as an atomic counter with no underflow
          protection, not as a contended boolean.

    Owned State:
        - `_tickets`: a deque whose LENGTH is the entire state. The elements are
          `None`; only the count carries meaning.

    Lifecycle / Cleanup:
        - `cleanup()` clears the deque, marks cleaned, and deletes the field.
        - NOT IDEMPOTENT, deliberately and by its own stated contract. A second
          call raises `AttributeError` because `_tickets` is already gone.
        - CONTRACT DIVERGENCE: `Cleanable` requires `cleanup()` to be idempotent.
          This class knowingly departs from that in exchange for hot-path
          cheapness. Flagged rather than silently inherited, because a caller
          writing generic `Cleanable` teardown will get a surprise here.

    Registration:
        USER-BINDABLE - deliberately unguarded. Owner ruling 2026-07-19: the
        switches are fair to expose. A user may legitimately hold or inject one
        as their own cheap flag, so it carries no sentinel.

    Subsystem Context:
        Part of `utilities/synchronization/`, in the switch family alongside
        `CounterSwitch` and `TicketFlag`. This is the cheapest member: no lock,
        no guard on the hot read, no underflow protection. Where `SafeGuard`
        coordinates locks and `PhaseLatch` coordinates completions, the switches
        just hold a count someone else interprets.

    System Context:
        A substrate primitive with no position in the DGR boot order. It exists
        for call sites where the cost of a lock would exceed the cost of the
        thing being guarded - which is why its contract pushes correctness onto
        the caller rather than absorbing it.
    """

    _ast_helper_access: str = "public"
    __agent_purpose__: str = (
        "access: public. Cheapest possible boolean/counter primitive, backed by "
        "deque ticket count. Truthy when at least one ticket exists. No lock, no "
        "underflow guard - set_false() on empty raises IndexError, and cleanup() "
        "is not idempotent. Use only where you own the invariant."
    )

    __slots__ = ("_tickets",)

    def __init__(self, value: bool = False) -> None:
        """
        Public API

        Initialize the switch with an optional truthy state.

        Args:
            value:
                When True, starts with one ticket (truthy).
                When False, starts empty (falsey).

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

        Release deque resources and break this primitive.

        Purpose:
            Explicitly tear down ticket storage for deterministic teardown in
            systems that aggressively clean runtime primitives.

        Contract:
            - Clears all tickets.
            - Marks this primitive cleaned.
            - Resets internal ticket storage to an empty deque.
            - No cleanup guard or idempotence check is applied; repeated cleanup
              is therefore unsupported by contract.

        Returns:
            None.
        """
        self._tickets.clear()
        self._cleaned = True
        del self._tickets

    def __bool__(self) -> bool:
        """
        Public API

        Return switch truth value based on ticket presence.

        Returns:
            bool:
                True when at least one ticket exists.

        Notes:
            This is the ONE genuinely unguarded method on the class - the hot
            read, kept free of a guard call on purpose.

        Raises:
            AttributeError: If the switch has been cleaned. `cleanup()` deletes
                `_tickets`, so truthiness on a dead switch raises rather than
                returning False. Do not use `bool(switch)` as a liveness probe.
        """
        return len(self._tickets) > 0

    def __len__(self) -> int:
        """
        Public API

        Return current ticket count.

        Returns:
            int:
                Number of active tickets.

        Raises:
            RuntimeError: If the switch has already been cleaned. Unlike
                `__bool__()`, this method DOES guard.
        """
        self.check_cleaned()
        return len(self._tickets)

    @property
    def value(self) -> bool:
        """
        Public API

        Boolean view over the current ticket count.

        Returns:
            bool:
                True when at least one ticket exists.

        Raises:
            RuntimeError: If the switch has already been cleaned. This property
                DOES guard, unlike the bare `__bool__()` it delegates to.
        """
        self.check_cleaned()
        return bool(self)

    @value.setter
    def value(self, new_value: bool) -> None:
        """
        Public API

        Set the switch state via ticket operations.

        Contract:
            - "True" appends one ticket.
            - "False" pops one ticket.
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

        Append one ticket to make/keep the switch truthy.

        Returns:
            None.
        """
        self.check_cleaned()
        self._tickets.append(None)

    def set_false(self) -> None:
        """
        Public API

        Pop one ticket to move the switch toward falsey state.

        Contract:
            - No underflow guard.
            - Empty-pop raises IndexError.

        Returns:
            None.
        """
        self.check_cleaned()
        self._tickets.pop()

    def clear_tickets(self) -> None:
        """
        Public API

        Remove all tickets and force falsey state.

        Returns:
            None.

        Notes:
            This is a force-clear operation; unlike `set_false()`, it does not
            remove tickets one at a time.
        """
        self.check_cleaned()
        self._tickets.clear()
