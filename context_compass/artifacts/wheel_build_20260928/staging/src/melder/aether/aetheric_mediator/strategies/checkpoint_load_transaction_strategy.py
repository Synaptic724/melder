"""
The whole-world load family: one thread takes everything.

Dependency-free beyond the standard library and this package.

This is the coarsest family in the vocabulary and it is coarse ON PURPOSE. It
mirrors the law crystallizer already enforces through the Aether `LoadGate`: one
load at a time, process-wide, and a second acquire from ANY thread refuses rather
than waits. Expressing that as `world` EXCLUSIVE is not a new restriction - it is
the existing restriction stated in the plane's vocabulary.
"""

from typing import Any, Dict, Mapping, TYPE_CHECKING

from melder.aether.aetheric_mediator.claim_mode import ClaimMode
from melder.aether.aetheric_mediator.identity import Identity
from melder.aether.aetheric_mediator.scope_keys import ScopeKey
from melder.aether.aetheric_mediator.transaction_strategy import TransactionStrategy

if TYPE_CHECKING:
    from melder.aether.aetheric_mediator.staged_transaction import (
        StagedTransaction,
    )


class CheckpointLoadTransactionStrategy(TransactionStrategy):
    """
    Claim the entire world for one checkpoint load.

    Purpose:
        Give a checkpoint replay the exclusivity it already takes, in a form the
        plane can arbitrate, report on, and hold alongside other claims.

    Contract:
        - Claims exactly one scope: `world`, EXCLUSIVE. Nothing else, because
          nothing else is needed - `world` excludes every other claim of every
          mode by the compatibility matrix, so naming additional scopes would be
          noise that makes the plan harder to read without changing what it
          isolates.
        - Metadata is not consulted. A checkpoint load's reach does not vary with
          its arguments: it rebuilds the world regardless of which checkpoint id
          it was handed. A family whose plan cannot vary should not pretend to
          read inputs.
        - PURE, like every `build_start_plan`.

    Scope proportionality:
        This family is allowed to be the blunt one. The alternative - enumerating
        every frame and subsystem a replay might touch - is both unknowable
        before the chain is folded and, once folded, equal to "all of them". A
        claim set that always evaluates to the whole world should say so
        directly.

    What this does NOT claim, and why:
        No `frame:` keys. A checkpoint load rebuilds frames, so it might look
        like it should claim each one. It does not need to: holding `world`
        EXCLUSIVE already excludes any claim on any frame. Listing them would
        also require knowing them up front, which is exactly the snapshot problem
        this plane exists to avoid.

    Threading:
        Stateless. Every hook is static; safe to dispatch from any thread.

    Lifecycle / Cleanup:
        NEVER INSTANTIATED. Registered as a class, per the `TransactionStrategy`
        contract, so there is no instance state and no `Cleanable` surface.

    Registration:
        MELDER KERNEL - guarded. Registered against
        `TransactionType.CHECKPOINT_LOAD`; never bound.

    Subsystem Context:
        The `world`-shaped member of the plane's own family set, alongside
        `FormationLoadTransactionStrategy` which is its frame-scoped counterpart.
        The pair is the whole point of having a scope vocabulary: the same
        subsystem's two load verbs claim differently because they reach
        differently.

    System Context:
        Crystallizer's `LoadGate` is not replaced by this and is not made
        redundant by it. The gate parks foreign threads at mediator new-root
        ingresses; this claim arbitrates between transactions on the plane. Until
        the wiring story rules otherwise both exist, and a load that takes this
        claim should still take the gate - the survey for that subsystem records
        that the gate covers a case claims do not, namely threads already past
        the ingress check.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Claims `world` exclusively for a checkpoint load.
        Melder kernel machinery: read it to understand the runtime, do not drive
        it directly.
    """

    @staticmethod
    def build_start_plan(
            *,
            submitter: Identity,
            metadata: Mapping[str, Any],
    ) -> Dict[str, ClaimMode]:
        """
        Return the whole-world exclusive claim set.

        Contract:
            PURE. Both arguments are accepted to satisfy the family contract and
            neither varies the plan; they are released rather than silently
            ignored so a reader can see the choice was deliberate.

        Args:
            submitter:
                The identity originating the transaction.
            metadata:
                Caller-supplied inputs. Unused by this family.

        Returns:
            Dict[str, ClaimMode]: `{world: EXCLUSIVE}`.
        """
        del submitter
        del metadata
        return {ScopeKey.world(): ClaimMode.EXCLUSIVE}

    @staticmethod
    def on_start(
            *,
            submitter: Identity,
            staged: "StagedTransaction",
    ) -> None:
        """
        Run family-local work after admission succeeds.

        Contract:
            No family-local work. The load itself is performed by the caller
            holding the claim, not by the strategy - a strategy that performed
            the operation would be the plane reaching into a subsystem, which
            this package must never do.

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
