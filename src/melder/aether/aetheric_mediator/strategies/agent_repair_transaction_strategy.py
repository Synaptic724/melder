"""
The repair family: the only one whose claim set is supplied, not derived.

Dependency-free beyond the standard library and this package.

This family is what makes `OutcomePolicy.LEAVE_BROKEN` mean something. That
policy leaves a half-built world in place as a WORK SURFACE for a repairing
agent rather than destroying it - and `TransactionType`'s own provenance note
draws the conclusion: an agent mending that world "is doing structural work and
must be able to claim it, or 'leave it for an agent' means 'leave it and stop the
world'".
"""

from typing import Any, Dict, Mapping, Tuple, TYPE_CHECKING

from melder.aether.aetheric_mediator.claim_mode import ClaimMode
from melder.aether.aetheric_mediator.identity import Identity
from melder.aether.aetheric_mediator.scope_keys import ScopeKey
from melder.aether.aetheric_mediator.transaction_strategy import TransactionStrategy

if TYPE_CHECKING:
    from melder.aether.aetheric_mediator.staged_transaction import (
        StagedTransaction,
    )


class AgentRepairTransactionStrategy(TransactionStrategy):
    """
    Claim exactly the scopes a repairing agent names.

    Purpose:
        Let an agent re-take the surface a broken transaction left behind, so
        repair is admitted work rather than an unmediated reach into a damaged
        world.

    Contract:
        - Claims `world` INTENT plus every scope key in metadata `repair_scopes`
          at EXCLUSIVE.
        - `repair_scopes` entries must be non-empty strings; non-conforming
          entries are SKIPPED, not coerced and not raised on.
        - When `repair_scopes` is absent, empty, or contains no usable entry,
          claims `world` EXCLUSIVE.
        - PURE. Reads metadata, mutates nothing.

    WHY THE CALLER SUPPLIES THE SCOPES, WHICH LOOKS LIKE A HOLE AND IS NOT:
        Every other family derives its plan from what the operation inherently
        reaches. Repair has no inherent reach - it reaches wherever the failure
        left residue, which is knowable only from the failed session's record.
        A `LEAVE_BROKEN` session records precisely that: the scopes it held and
        the described rollback actions it deliberately did not run. So
        `repair_scopes` is not a caller's guess, it is a READ-BACK of the broken
        session's own granted scopes.

        Deriving it inside this strategy would require the strategy to reach into
        session state, and `build_start_plan` is pure by contract and runs before
        admission. Passing it through metadata keeps the purity and puts the
        lookup where it belongs - in whoever assembles the repair request.

    WHY THE FALLBACK IS WHOLE-WORLD EXCLUSIVE, and it is not a convenience:
        An agent that cannot say what it is repairing is about to touch an
        unknown part of a world already known to be broken. That is the single
        most dangerous transaction this plane can admit, and the only safe claim
        for unbounded reach into damaged state is all of it. This branch should
        be rare and loud; if it is common, the repair request assembler is not
        reading the broken session's granted scopes and that is the bug.

    Scope proportionality:
        Deliberately UNBOUNDED in count - a repair may legitimately name many
        scopes, because a broken transaction may have held many. Each is claimed
        EXCLUSIVE because repair rewrites what it touches. The `world` INTENT
        marker sits above them for the same reason it does elsewhere: so a
        whole-world operation cannot run while a repair is in flight.

    JURISDICTION still applies:
        Nothing here validates that a supplied scope key belongs to this plane's
        vocabulary, because the claim table matches on strings and an unknown key
        simply isolates itself harmlessly. But a caller that passes frame-internal
        keys is asking the wrong plane for isolation - the frame's own admission
        authority owns those, and a claim taken here will not exclude anything
        that plane admits. See the package docstring.

    Threading:
        Stateless. Every hook is static; safe to dispatch from any thread.

    Lifecycle / Cleanup:
        NEVER INSTANTIATED. Registered as a class; no instance state, no
        `Cleanable` surface.

    Registration:
        MELDER KERNEL - guarded. Registered against `TransactionType.AGENT_REPAIR`;
        never bound.

    Subsystem Context:
        The counterpart to `SessionStatus.BROKEN`. That status exists as a
        distinct terminal state - deliberately not a flavour of `ABORTED` -
        because aborted means the world was returned toward its prior shape while
        broken means it was knowingly left mid-flight. This family is what the
        agent uses to act on that distinction.

    System Context:
        A repair transaction is itself a transaction and can itself fail. If it
        does, and it too runs under `LEAVE_BROKEN`, the residue compounds. That
        is a policy question for whoever assembles repair requests rather than a
        claim question, and this family does not attempt to answer it.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Claims exactly the scopes a repairing agent names,
        falling back to whole-world exclusivity when it names none. Melder kernel
        machinery: read it to understand the runtime, do not drive it directly.
    """

    METADATA_REPAIR_SCOPES = "repair_scopes"

    @staticmethod
    def _usable_scope_keys(candidate: Any) -> Tuple[str, ...]:
        """
        Internal

        Return the non-empty string scope keys from a supplied candidate.

        Contract:
            - Accepts any iterable of values; a non-iterable candidate yields an
              empty tuple rather than raising.
            - A `str` candidate yields an EMPTY tuple. Iterating a bare string
              would silently claim one scope per character, which is the kind of
              quiet nonsense a claim planner must never produce.
            - Order is preserved and duplicates are dropped, first occurrence
              winning, so a repeated key cannot make the plan depend on how many
              times it was listed.

        Args:
            candidate:
                The raw metadata value.

        Returns:
            Tuple[str, ...]: Usable scope keys, in first-seen order.
        """
        if isinstance(candidate, str):
            return tuple()
        try:
            entries = list(candidate)
        except TypeError:
            return tuple()
        seen = set()
        usable = []
        for entry in entries:
            if not isinstance(entry, str) or not entry:
                continue
            if entry in seen:
                continue
            seen.add(entry)
            usable.append(entry)
        return tuple(usable)

    @staticmethod
    def build_start_plan(
            *,
            submitter: Identity,
            metadata: Mapping[str, Any],
    ) -> Dict[str, ClaimMode]:
        """
        Return the supplied repair claim set, or the whole-world set when none.

        Contract:
            PURE. Malformed entries are skipped rather than raised on, so one bad
            entry cannot refuse a repair of an already-damaged world; the
            whole-world fallback covers the case where nothing usable remains.

        Args:
            submitter:
                The identity originating the transaction.
            metadata:
                Caller-supplied inputs. `repair_scopes` carries the scope keys
                read back from the broken session's granted scopes.

        Returns:
            Dict[str, ClaimMode]:
                `{world: INTENT, <each repair scope>: EXCLUSIVE}` when at least
                one usable scope was supplied; otherwise `{world: EXCLUSIVE}`.
        """
        del submitter
        repair_scopes = AgentRepairTransactionStrategy._usable_scope_keys(
            metadata.get(AgentRepairTransactionStrategy.METADATA_REPAIR_SCOPES)
        )
        if not repair_scopes:
            return {ScopeKey.world(): ClaimMode.EXCLUSIVE}
        plan = {ScopeKey.world(): ClaimMode.INTENT}
        for scope_key in repair_scopes:
            plan[scope_key] = ClaimMode.EXCLUSIVE
        return plan

    @staticmethod
    def on_start(
            *,
            submitter: Identity,
            staged: "StagedTransaction",
    ) -> None:
        """
        Run family-local work after admission succeeds.

        Contract:
            No family-local work; the repair is performed by the claim holder.

        Args:
            submitter:
                The identity originating the transaction.
            staged:
                The immutable post-admission record.

        Returns:
            None.
        """
        del submitter
        del staged
        return None

    @staticmethod
    def on_end(
            *,
            submitter: Identity,
            staged: "StagedTransaction",
    ) -> None:
        """
        Run family-local work during finalisation.

        Contract:
            No family-local work, on either the commit or the failure path.

        Args:
            submitter:
                The identity originating the transaction.
            staged:
                The immutable post-admission record.

        Returns:
            None.
        """
        del submitter
        del staged
        return None
