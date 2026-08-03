"""
The activation family: the edge the owner named as the wiring gate.

Dependency-free beyond the standard library and this package.

Owner constraint 6 gates participation on activation - a subsystem takes part in
the plane ONLY when enabled and active, and emits its basic conditions at that
edge. This family is that edge, which makes it the one whose claim must be held
while the subsystem is still deciding whether it is on.
"""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from melder.aether.aetheric_mediator.claim_mode import ClaimMode
from melder.aether.aetheric_mediator.identity import Identity
from melder.aether.aetheric_mediator.scope_keys import ScopeKey
from melder.aether.aetheric_mediator.transaction_strategy import TransactionStrategy

if TYPE_CHECKING:
    from melder.aether.aetheric_mediator.staged_transaction import (
        StagedTransaction,
    )


class SubsystemEnableTransactionStrategy(TransactionStrategy):
    """
    Claim one subsystem exclusively for its activation transition.

    Purpose:
        Make a subsystem's enable transition a transaction, so its basic
        conditions land on the plane atomically rather than while another
        transaction is already reasoning about a half-enabled subsystem.

    Contract:
        - When metadata carries a non-empty string `subsystem_name`, claims
          `world` INTENT plus `subsystem:<subsystem_name>` EXCLUSIVE.
        - Otherwise claims `world` EXCLUSIVE - an activation whose subject is
          unknown could be any subsystem, and the honest claim for that is all of
          them.
        - PURE. Reads metadata, mutates nothing.

    The parent/child pair:
        `world` INTENT with `subsystem:<name>` EXCLUSIVE is the same shape the
        formation-load family uses one level down. Two different subsystems
        enable in parallel - disjoint child keys, coexisting intent markers -
        while a checkpoint load asking for `world` EXCLUSIVE is excluded by
        either. That last exclusion matters more than it looks: a whole-world
        replay running against a subsystem mid-activation would observe a
        subsystem that is neither off nor on.

    Why EXCLUSIVE on the subsystem and not INTENT:
        Enable is a whole-unit write. It installs policy, flips a lifecycle flag
        and emits basic conditions - there is no piece-work beneath it that
        another holder could safely do concurrently. A second enable of the same
        subsystem is not concurrency, it is a caller bug, and EXCLUSIVE turns it
        into a refusal with evidence rather than a race.

    Threading:
        Stateless. Every hook is static; safe to dispatch from any thread.

    Lifecycle / Cleanup:
        NEVER INSTANTIATED. Registered as a class; no instance state, no
        `Cleanable` surface.

    Registration:
        MELDER KERNEL - guarded. Registered against
        `TransactionType.SUBSYSTEM_ENABLE`; never bound.

    Subsystem Context:
        Paired with `SubsystemDisableTransactionStrategy`, which is its exact
        inverse and claims identically because the two transitions write the same
        surface in opposite directions.

    System Context:
        The three subsystems reach this edge differently - crystallizer through
        `activate()`, nexus through `enable()`, MR through `activate()` with
        hydration ordered BEFORE the flag flip. The plane does not model that
        difference and must not: what it isolates is the transition, not how each
        subsystem performs it.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Claims one subsystem exclusively under a world intent
        marker for its enable transition. Melder kernel machinery: read it to
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
            SubsystemEnableTransactionStrategy.METADATA_SUBSYSTEM_NAME
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
            staged: StagedTransaction,
    ) -> None:
        """
        Run family-local work after admission succeeds.

        Contract:
            No family-local work. The subsystem performs its own activation and
            emits its own basic conditions; a strategy that did either would be
            the plane reaching into a subsystem.

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

    @staticmethod
    def on_end(
            *,
            submitter: Identity,
            staged: StagedTransaction,
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
