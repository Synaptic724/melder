"""
The deactivation family: the inverse edge, and the harder one.

Dependency-free beyond the standard library and this package.

Enable and disable claim identically because they write the same surface. They
are not equally safe, and that asymmetry is documented on the class rather than
hidden by the symmetry of their claim sets.
"""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from melder.aether.aetheric_mediator.claim_mode import ClaimMode
from melder.aether.aetheric_mediator.identity import Identity
from melder.aether.aetheric_mediator.participation import ParticipationState
from melder.aether.aetheric_mediator.scope_keys import ScopeKey
from melder.aether.aetheric_mediator.transaction_strategy import TransactionStrategy

if TYPE_CHECKING:
    from melder.aether.aetheric_mediator.information_registry import (
        InformationRegistry,
    )
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
        - Claim set is IDENTICAL to `SubsystemEnableTransactionStrategy` and to
          `SubsystemConfigureTransactionStrategy`. Three families with one claim
          shape is correct here and is not a candidate for merging: they are
          distinct vocabulary members, they stamp distinct fact families, and
          above all they write DIFFERENT PARTICIPATION STATES at commit.
          Reporting that could not tell an enable from a disable would be
          useless for exactly the incident where it is needed.

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
        brackets the only span in which a subsystem EMITS: outside those two
        edges it may still be known to the plane, but it is not participating,
        per owner constraint 6.

    System Context:
        Disable is the edge where a subsystem's basic conditions STOP being
        true. Anything the plane cached from them - and the information registry
        does cache fact baselines - is stale from this transaction's commit
        onward. `apply_commit_delta` stamps a fresh baseline for the region
        before moving the state, which is what lets a later reader notice the
        transition happened rather than trusting a baseline taken while the
        subsystem was live.

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
    ) -> dict[str, ClaimMode]:
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

    @classmethod
    def apply_commit_delta(
            cls,
            *,
            information_registry: "InformationRegistry",
            submitter: Identity,
            staged: "StagedTransaction",
    ) -> None:
        """
        Move the subsystem to DISABLED - it ran, and it stopped.

        Purpose:
            The exact inverse of the enable family's delta, and the reason these
            two families are not one. They claim identically; they differ
            entirely in what they write at commit.

        Contract:
            - Runs at commit WHILE CLAIMS ARE STILL HELD, so no reader can
              observe a subsystem that has stopped participating but still
              reads as emitting.
            - Calls the base delta first, stamping the fact baseline. That
              baseline is what lets a later reader notice the transition
              happened rather than trusting one taken while the subsystem was
              live.
            - RECORDS `DISABLED` RATHER THAN DELETING THE ROW. Deleting was the
              first shape of this and it was wrong: it made a subsystem that
              was switched off deliberately indistinguishable from one nobody
              ever wired in, and those have completely different fixes. The row
              stays so the plane can say which of the two happened.
            - PASSES NO CONDITIONS, which KEEPS the ones the subsystem was last
              running with. That retention is safe ONLY because the state now
              guards them: `is_participating` reads False for a DISABLED row,
              so nothing treats them as live settings, while "what was it
              running with when it stopped" stays answerable. In a store that
              recorded presence alone this would be exactly the stale-policy
              hazard that argued for deletion.
            - Disabling a subsystem the plane never heard of CREATES the row at
              DISABLED rather than erroring. A disable arriving without a prior
              enable is odd but not dangerous, and it is still a fact.

        WHAT THIS STILL DOES NOT DO, unchanged and worth repeating here because
        the commit delta makes it look more complete than it is:
            Writing DISABLED does not QUIESCE the subsystem. Work already
            running inside it never asked the plane for anything and is not
            stopped by anything the plane does. The claim excludes transactions;
            the delta records a fact. Neither drains. That still belongs to the
            subsystem's own gate, exactly as the crystallizer load pairs its
            claim with the `LoadGate`.

        Args:
            information_registry: The plane registry to write.
            submitter: The identity originating the transaction.
            staged: The immutable post-admission record.

        Returns:
            None.
        """
        super().apply_commit_delta(
            information_registry=information_registry,
            submitter=submitter,
            staged=staged,
        )
        subsystem_name = staged.metadata.get(cls.METADATA_SUBSYSTEM_NAME)
        if not isinstance(subsystem_name, str) or not subsystem_name:
            return
        information_registry.set_participation(
            subsystem_name=subsystem_name,
            state=ParticipationState.DISABLED,
            reporter=staged.request_id,
        )
