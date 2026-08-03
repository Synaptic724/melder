"""
The deactivation family: the inverse edge, and the harder one.

Dependency-free beyond the standard library and this package.

Enable and disable claim identically because they write the same surface. They
are not equally safe, and that asymmetry is documented on the class rather than
hidden by the symmetry of their claim sets.
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


class SubsystemDisableTransactionStrategy(TransactionStrategy):
    """
    Claim one subsystem exclusively for its deactivation transition.

    Purpose:
        Make a subsystem's disable transition a transaction, so nothing admits
        against a subsystem that is in the middle of switching off.

    Contract:
        - When metadata carries a non-empty string `subsystem_name`, claims
          `world` INTENT plus `subsystem:<subsystem_name>` EXCLUSIVE.
        - Otherwise claims `world` EXCLUSIVE.
        - PURE. Reads metadata, mutates nothing.
        - Claim set is IDENTICAL to `SubsystemEnableTransactionStrategy`. Two
          families with one claim shape is correct here and is not a candidate
          for merging: they are distinct vocabulary members, they stamp distinct
          fact families through the default commit delta, and reporting that
          could not tell an enable from a disable would be useless for exactly
          the incident where it is needed.

    WHAT THE CLAIM DOES NOT BUY, and this is the part worth reading:
        The claim excludes other TRANSACTIONS from the subsystem. It does not
        quiesce work already running INSIDE it. The subsystem survey found this
        directly: MR's `deactivate` flips its activated flag without draining
        in-flight set verbs, and Nexus's gate population is invisible to any
        claim table because parked threads wait on an event rather than on a
        scope.

        So a disable can admit, hold an uncontested exclusive claim, and still
        switch off underneath live work - because that work never asked the plane
        for anything. Holding the claim is necessary and not sufficient. Whoever
        wires this must pair it with the subsystem's own drain, exactly as the
        crystallizer load pairs its claim with the `LoadGate`.

    Threading:
        Stateless. Every hook is static; safe to dispatch from any thread.

    Lifecycle / Cleanup:
        NEVER INSTANTIATED. Registered as a class; no instance state, no
        `Cleanable` surface.

    Registration:
        MELDER KERNEL - guarded. Registered against
        `TransactionType.SUBSYSTEM_DISABLE`; never bound.

    Subsystem Context:
        The exact inverse of `SubsystemEnableTransactionStrategy`. The pair
        brackets a subsystem's participation in the plane: outside the two edges
        a subsystem is not a participant at all, per owner constraint 6.

    System Context:
        Disable is the edge where a subsystem's basic conditions STOP being true.
        Anything the plane cached from them - and the information registry does
        cache fact baselines - is stale from this transaction's commit onward.
        The default `apply_commit_delta` stamps a fresh baseline for the region,
        which is what lets a later reader notice the transition happened rather
        than trusting a baseline taken while the subsystem was live.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Claims one subsystem exclusively under a world intent
        marker for its disable transition; the claim excludes transactions, not
        work already inside the subsystem. Melder kernel machinery: read it to
        understand the runtime, do not drive it directly.
    """

    METADATA_SUBSYSTEM_NAME = "subsystem_name"

    @staticmethod
    def build_start_plan(
            *,
            submitter: Identity,
            metadata: Mapping[str, Any],
    ) -> Dict[str, ClaimMode]:
        """
        Return the subsystem-scoped claim set, or the whole-world set when unknown.

        Contract:
            PURE. A `subsystem_name` present but not a non-empty string is
            treated as ABSENT and degrades to the larger claim.

        Args:
            submitter:
                The identity originating the transaction.
            metadata:
                Caller-supplied inputs. `subsystem_name` selects the subsystem.

        Returns:
            Dict[str, ClaimMode]:
                `{world: INTENT, subsystem:<name>: EXCLUSIVE}` when the subsystem
                is known; otherwise `{world: EXCLUSIVE}`.
        """
        del submitter
        subsystem_name = metadata.get(
            SubsystemDisableTransactionStrategy.METADATA_SUBSYSTEM_NAME
        )
        if not isinstance(subsystem_name, str) or not subsystem_name:
            return {ScopeKey.world(): ClaimMode.EXCLUSIVE}
        return {
            ScopeKey.world(): ClaimMode.INTENT,
            ScopeKey.subsystem(subsystem_name): ClaimMode.EXCLUSIVE,
        }

    @staticmethod
    def on_start(
            *,
            submitter: Identity,
            staged: "StagedTransaction",
    ) -> None:
        """
        Run family-local work after admission succeeds.

        Contract:
            No family-local work. In particular this hook does NOT drain the
            subsystem - the plane has no reach into subsystem internals and the
            drain belongs to whoever owns them.

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
