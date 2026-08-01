"""
The scope-claim table for the mediator plane.

Dependency rule (non-negotiable, epic constraint 4): this module imports the
standard library and `melder.utilities` ONLY. It must never reach into
`melder.aether`, because the plane is constructed before any `AethericFrame`
can exist and must stay testable in isolation.

Modelled on the working `ChangeControlEmbargoManager`: atomic all-or-nothing
acquisition over a set of scope keys, mode-aware coexistence, blocking evidence
naming a real holder, and release/cleanup that always wakes waiters.
"""

import threading
import time
from typing import Dict, List, Mapping, Tuple

from melder.aether.aetheric_mediator.identity import Identity
from melder.aether.aetheric_mediator.claim_mode import ClaimCompatibility, ClaimMode
from melder.utilities.general_base.cleanable import Cleanable


class ClaimBlock:
    """
    One reason an acquisition could not be granted.

    Purpose:
        Carry actionable blocking evidence out of a refused or timed-out
        acquisition: which scope, held by whom, in what mode.

    Contract:
        Immutable. Produced by the table, consumed by callers building an
        error message. Never mutated after construction.

    Registration:
        MELDER KERNEL - guarded. Diagnostic value object; never bound.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Blocking evidence for a refused scope claim -
        names the scope, the holder, and the held mode.
    """

    __slots__ = ["_scope_key", "_holder", "_held_mode", "_requested_mode"]

    def __init__(
            self,
            *,
            scope_key: str,
            holder: Identity,
            held_mode: ClaimMode,
            requested_mode: ClaimMode,
    ) -> None:
        """
        Build one immutable blocking record.

        Args:
            scope_key:
                The contested scope key.
            holder:
                The identity currently holding the scope.
            held_mode:
                The mode the holder holds it in.
            requested_mode:
                The mode that was refused.

        Returns:
            None.
        """
        self._scope_key: str = scope_key
        self._holder: Identity = holder
        self._held_mode: ClaimMode = held_mode
        self._requested_mode: ClaimMode = requested_mode

    @property
    def scope_key(self) -> str:
        """Return the contested scope key."""
        return self._scope_key

    @property
    def holder(self) -> Identity:
        """Return the identity currently holding the scope."""
        return self._holder

    @property
    def held_mode(self) -> ClaimMode:
        """Return the mode the scope is currently held in."""
        return self._held_mode

    @property
    def requested_mode(self) -> ClaimMode:
        """Return the mode that was refused."""
        return self._requested_mode

    def describe(self) -> str:
        """
        Render this block for an error message.

        Returns:
            str: A one-line rendering naming scope, holder, and both modes.
        """
        return "{0} held {1} by {2} (requested {3})".format(
            self._scope_key,
            self._held_mode.value,
            self._holder.describe(),
            self._requested_mode.value,
        )


class _GrantedClaim:
    """
    One granted claim on one scope key.

    Contract:
        Internal to the table. Mode is replaced only through the table's own
        grant path, never mutated by callers.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Table-owned record of one granted scope claim.
    """

    __slots__ = ["holder", "mode"]

    def __init__(self, *, holder: Identity, mode: ClaimMode) -> None:
        """
        Build one granted-claim record.

        Args:
            holder: The identity granted the claim.
            mode: The granted mode.

        Returns:
            None.
        """
        self.holder: Identity = holder
        self.mode: ClaimMode = mode


class ClaimTable(Cleanable):
    """
    Atomic, mode-aware scope-claim table for the mediator plane.

    Purpose:
        Serialise structural work across subsystems by scope rather than
        globally, so disjoint work proceeds in parallel and only true
        overlap waits.

    Contract:
        - ACQUISITION IS ALL-OR-NOTHING. A request either takes every scope
          it asked for or takes none. There is no partial grant, so a caller
          can never hold half a claim set and believe it is isolated.
        - RE-ENTRY IS A NO-OP, NOT AN UPGRADE. A holder re-claiming a scope
          it already holds keeps its EXISTING mode. Mode upgrades are
          deliberately unimplemented in this slice: upgrading while peers
          hold compatible claims is the classic deadlock shape and deserves
          an explicit design, not an accident. Requesting a stronger mode on
          a scope you already hold silently keeps the weaker one - callers
          needing an upgrade must release and re-acquire.
        - REFUSAL IS EVIDENCED. `try_acquire` returns `ClaimBlock` records
          naming scope, holder and modes; it never returns a bare False.
        - RELEASE AND CLEANUP ALWAYS NOTIFY. Every path that could unblock a
          waiter calls `notify_all`, including cleanup, so no thread can be
          left parked on a dead table.

    Owned State:
        `_claims` (scope key -> granted claims) and one `Condition` bound to
        an `RLock`. Nothing else; the table holds no subsystem references.

    Lifecycle / Cleanup:
        Idempotent. Cleanup wakes every waiter BEFORE dropping state, so
        parked threads observe a cleaned table and exit rather than hang.

    Threading:
        All public methods take the table lock. Waiting happens on the
        condition, which releases the lock while parked. The table never
        calls out to foreign code while holding the lock, so it cannot be
        the inner half of an AB-BA against a subsystem lock.

    Registration:
        MELDER KERNEL - guarded. Constructed by the plane; never bound.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Atomic mode-aware scope-claim table. Grants all
        requested scopes or none, with named blocking evidence on refusal.
    """

    __slots__ = Cleanable.__slots__ + ["_claims", "_condition"]

    def __init__(self) -> None:
        """
        Build one empty claim table.

        Returns:
            None.
        """
        super().__init__()
        self._claims: Dict[str, List[_GrantedClaim]] = {}
        self._condition: threading.Condition = threading.Condition(
            threading.RLock()
        )

    def cleanup(self) -> None:
        """
        Idempotently drop all claims and wake every waiter.

        Contract:
            Waiters are notified BEFORE state is dropped so they wake, see a
            cleaned table, and exit rather than parking forever.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._condition:
            # RE-CHECK UNDER THE LOCK. The check above is only a cheap fast
            # path; without this second check two threads can both pass it,
            # both enter here, and both fall through to the deletions below -
            # the second raising AttributeError on an already-deleted slot.
            # Free-threaded 3.14t removes the accidental serialisation that
            # used to hide this.
            if self._cleaned:
                return
            self._cleaned = True
            self._claims.clear()
            self._condition.notify_all()
        del self._claims
        del self._condition

    def try_acquire(
            self,
            holder: Identity,
            requested: Mapping[str, ClaimMode],
    ) -> Tuple[ClaimBlock, ...]:
        """
        Attempt one atomic all-or-nothing acquisition.

        Contract:
            Grants every requested scope or none. Returns an EMPTY tuple on
            success; a non-empty tuple is the full set of blocking reasons.

        Args:
            holder:
                The identity requesting the claims.
            requested:
                Scope key -> requested mode. An empty mapping is a
                successful no-op.

        Returns:
            Tuple[ClaimBlock, ...]:
                Empty on success, otherwise every block that refused it.

        Raises:
            RuntimeError: If the table has been cleaned.
        """
        self.check_cleaned()
        with self._condition:
            blocks = self._collect_blocks(holder, requested)
            if blocks:
                return blocks
            self._grant(holder, requested)
            return ()

    def acquire(
            self,
            holder: Identity,
            requested: Mapping[str, ClaimMode],
            timeout_seconds: float,
    ) -> None:
        """
        Acquire atomically, waiting up to `timeout_seconds` for passage.

        Contract:
            Retries on every notification until granted or the deadline
            passes. On timeout it raises with the CURRENT blocking evidence,
            which is the information a caller or agent needs to act.

        Args:
            holder:
                The identity requesting the claims.
            requested:
                Scope key -> requested mode.
            timeout_seconds:
                Maximum wait. Must be non-negative; zero means try once.

        Returns:
            None.

        Raises:
            ValueError: If `timeout_seconds` is negative.
            RuntimeError: If the table is cleaned, is cleaned while waiting,
                or the deadline passes. The timeout message names every
                blocking scope and holder.
        """
        self.check_cleaned()
        if timeout_seconds < 0:
            raise ValueError(
                "timeout_seconds must be non-negative; got {0!r}.".format(
                    timeout_seconds
                )
            )
        deadline = time.monotonic() + timeout_seconds
        with self._condition:
            while True:
                if self._cleaned:
                    raise RuntimeError(
                        "ClaimTable was cleaned while {0} waited for "
                        "passage.".format(holder.describe())
                    )
                blocks = self._collect_blocks(holder, requested)
                if not blocks:
                    self._grant(holder, requested)
                    return
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise RuntimeError(
                        "ClaimTable acquisition timed out after {0}s "
                        "for {1}; blocked by: {2}".format(
                            timeout_seconds,
                            holder.describe(),
                            "; ".join(block.describe() for block in blocks),
                        )
                    )
                self._condition.wait(timeout=remaining)

    def release_holder(self, holder: Identity) -> int:
        """
        Release every claim held by `holder` and wake waiters.

        Contract:
            Idempotent: releasing a holder that holds nothing is a no-op
            returning zero. Always notifies, because a release is the main
            event a waiter is parked on.

        Args:
            holder:
                The identity whose claims are released.

        Returns:
            int: How many scope claims were released.

        Raises:
            RuntimeError: If the table has been cleaned.
        """
        self.check_cleaned()
        released = 0
        with self._condition:
            for scope_key in list(self._claims.keys()):
                remaining = [
                    claim
                    for claim in self._claims[scope_key]
                    if claim.holder != holder
                ]
                released += len(self._claims[scope_key]) - len(remaining)
                if remaining:
                    self._claims[scope_key] = remaining
                else:
                    del self._claims[scope_key]
            self._condition.notify_all()
        return released

    def wait_for_change(self, timeout_seconds: float) -> bool:
        """
        Park until some claim is released, or until `timeout_seconds` passes.

        Purpose:
            Let a bounded retry loop OUTSIDE this table wait efficiently
            instead of polling. The admission orchestrator must not hold its
            own admission lock while waiting - doing so would block every
            other admission behind one contended request - so it releases
            that lock and parks here instead.

        Contract:
            - Waits on the table's own condition, so a waiter wakes on the
              next release or cleanup rather than on a timer.
            - Returns promptly and truthfully if the table is cleaned while
              parked; callers must re-check state after waking and must not
              assume a wake means their claims are now free.
            - This is a NOTIFICATION primitive, not an acquisition. It grants
              nothing.

        Args:
            timeout_seconds: Maximum time to park. Must be non-negative.

        Returns:
            bool: True if woken by a notification, False on timeout.

        Raises:
            ValueError: If `timeout_seconds` is negative.
            RuntimeError: If the table has been cleaned before waiting.
        """
        self.check_cleaned()
        if timeout_seconds < 0:
            raise ValueError(
                "timeout_seconds must be non-negative; got {0!r}.".format(
                    timeout_seconds
                )
            )
        with self._condition:
            if self._cleaned:
                return False
            return self._condition.wait(timeout=timeout_seconds)

    def held_scopes(self, holder: Identity) -> Tuple[str, ...]:
        """
        Return the scope keys currently held by `holder`, sorted.

        Args:
            holder:
                The identity to inspect.

        Returns:
            Tuple[str, ...]: Sorted scope keys, empty when none are held.

        Raises:
            RuntimeError: If the table has been cleaned.
        """
        self.check_cleaned()
        with self._condition:
            return tuple(
                sorted(
                    scope_key
                    for scope_key, claims in self._claims.items()
                    if any(claim.holder == holder for claim in claims)
                )
            )

    def describe(self) -> Dict[str, object]:
        """
        Return a detached snapshot of the table for diagnostics.

        Contract:
            Fully detached: contains only strings and ints, no live holder
            references, so it is safe to log, ship, or serialise.

        Returns:
            Dict[str, object]:
                `scope_count` plus `scopes` mapping each key to its granted
                `(holder_description, mode_value)` pairs.

        Raises:
            RuntimeError: If the table has been cleaned.
        """
        self.check_cleaned()
        with self._condition:
            scopes: Dict[str, object] = {
                scope_key: [
                    [claim.holder.describe(), claim.mode.value]
                    for claim in claims
                ]
                for scope_key, claims in self._claims.items()
            }
            return {"scope_count": len(self._claims), "scopes": scopes}

    def _collect_blocks(
            self,
            holder: Identity,
            requested: Mapping[str, ClaimMode],
    ) -> Tuple[ClaimBlock, ...]:
        """
        Collect every reason `requested` cannot be granted to `holder`.

        Contract:
            Caller MUST hold the condition. Collects ALL blocks rather than
            short-circuiting on the first, so a timeout can name every
            contested scope instead of one at a time.
            A holder never blocks itself: its own existing claims are
            skipped.

        Args:
            holder: The requesting identity.
            requested: Scope key -> requested mode.

        Returns:
            Tuple[ClaimBlock, ...]: Empty when the request may be granted.
        """
        blocks: List[ClaimBlock] = []
        for scope_key, requested_mode in requested.items():
            for claim in self._claims.get(scope_key, ()):
                if claim.holder == holder:
                    continue
                if ClaimCompatibility.permits(claim.mode, requested_mode):
                    continue
                blocks.append(
                    ClaimBlock(
                        scope_key=scope_key,
                        holder=claim.holder,
                        held_mode=claim.mode,
                        requested_mode=requested_mode,
                    )
                )
        return tuple(blocks)

    def _grant(
            self,
            holder: Identity,
            requested: Mapping[str, ClaimMode],
    ) -> None:
        """
        Record every requested claim for `holder`.

        Contract:
            Caller MUST hold the condition and MUST have confirmed via
            `_collect_blocks` that the request is grantable. Re-entry keeps
            the holder's EXISTING mode - see the class contract on why
            upgrades are not implemented here.

        Args:
            holder: The identity being granted.
            requested: Scope key -> requested mode.

        Returns:
            None.
        """
        for scope_key, requested_mode in requested.items():
            claims = self._claims.setdefault(scope_key, [])
            if any(claim.holder == holder for claim in claims):
                continue
            claims.append(_GrantedClaim(holder=holder, mode=requested_mode))
