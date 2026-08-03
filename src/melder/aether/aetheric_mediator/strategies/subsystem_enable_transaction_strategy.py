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
from melder.aether.aetheric_mediator.participation import (
    ParticipationConditions,
    ParticipationState,
)
from melder.aether.aetheric_mediator.scope_keys import ScopeKey
from melder.aether.aetheric_mediator.transaction_strategy import TransactionStrategy

if TYPE_CHECKING:
    from melder.aether.aetheric_mediator.information_registry import (
        InformationRegistry,
    )
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
        One of three lifecycle families - configure, enable, disable - that all
        claim identically because they write the same surface. This is the only
        one of the three that produces an emitting subsystem; the other two both
        leave it silent, for different reasons and from different states.

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

    @classmethod
    def apply_commit_delta(
            cls,
            *,
            information_registry: "InformationRegistry",
            submitter: Identity,
            staged: "StagedTransaction",
    ) -> None:
        """
        Move the subsystem to ENABLED - the one state that emits.

        Purpose:
            This is where an enable stops being a claim and becomes a fact. The
            plane cannot ask a subsystem whether it is active - it is forbidden
            to import one - so the subsystem announces itself here and the
            answer is stored.

        WHY THIS OVERRIDE EXISTS AT ALL:
            Enable, disable and configure claim IDENTICALLY - `world` INTENT
            plus `subsystem:<name>` EXCLUSIVE. If the claim were the only thing
            a family expressed, the three would be indistinguishable, and a
            strategy layer that cannot tell "switch on" from "switch off" is a
            lookup table wearing a class. The difference lives HERE, in the
            state each writes at commit.

        Contract:
            - Runs at commit WHILE CLAIMS ARE STILL HELD, so the state change
              lands atomically with the transition that produced it. A reader
              cannot observe a subsystem that is admitted-but-not-yet-recorded.
            - Calls the base delta FIRST so the fact baseline is stamped, then
              moves the state. Order matters only for readers that check
              freshness before participation, but it is fixed rather than
              incidental.
            - THIS IS THE ONLY EDGE THAT MAKES A SUBSYSTEM EMIT.
              `ParticipationState.ENABLED` is the sole state for which `emits`
              is True, and nothing else in the plane writes it.
            - PASSES CONDITIONS ONLY WHEN THE ENABLE ANNOUNCED SOME. An enable
              that declares nothing passes `None`, which KEEPS whatever a prior
              configure recorded. Passing an empty mapping instead would erase
              it, and the configure-then-enable sequence - the normal one -
              would lose its settings at the moment the subsystem started.
            - Reads ONLY the keys `ParticipationConditions` declares, so a
              subsystem cannot widen its own row by adding metadata keys.
            - Failures PROPAGATE and poison the commit, per the base contract. A
              state change that silently failed to write would leave the plane
              believing a subsystem is off while it is running.

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
            # An enable whose subject is unknown took `world` EXCLUSIVE and is
            # a caller error, but it is not this hook's job to refuse a
            # transaction that admission already accepted. Nothing is recorded,
            # which leaves the participant store honest.
            return
        announced = ParticipationConditions.select(staged.metadata)
        information_registry.set_participation(
            subsystem_name=subsystem_name,
            state=ParticipationState.ENABLED,
            reporter=staged.request_id,
            conditions=announced if announced else None,
        )
