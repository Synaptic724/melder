"""
The configuration family: declaring how a subsystem would run, without running.

Dependency-free beyond the standard library and this package.

Owner constraint 6 gates participation on activation. That leaves a real gap the
plane had no way to express: a subsystem whose settings are known but which has
never been switched on. Before this family, that subsystem was indistinguishable
from one nobody had ever wired in - both were simply absent from the store - and
those two situations have completely different fixes.
"""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from melder.aether.aetheric_mediator.claim_mode import ClaimMode
from melder.aether.aetheric_mediator.identity import Identity
from melder.aether.aetheric_mediator.participation import ParticipationConditions
from melder.aether.aetheric_mediator.scope_keys import ScopeKey
from melder.aether.aetheric_mediator.transaction_strategy import TransactionStrategy

if TYPE_CHECKING:
    from melder.aether.aetheric_mediator.information_registry import (
        InformationRegistry,
    )
    from melder.aether.aetheric_mediator.staged_transaction import (
        StagedTransaction,
    )


class SubsystemConfigureTransactionStrategy(TransactionStrategy):
    """
    Claim one subsystem exclusively while its basic conditions are recorded.

    Purpose:
        Let a subsystem declare how it would run as its own transaction, so the
        plane can distinguish "configured but not started" from both "running"
        and "never heard of it".

    Contract:
        - When metadata carries a non-empty string `subsystem_name`, claims
          `world` INTENT plus `subsystem:<subsystem_name>` EXCLUSIVE.
        - Otherwise claims `world` EXCLUSIVE, on the same unknown-reach
          reasoning every other family here uses.
        - PURE. Reads metadata, mutates nothing.

    THE CLAIM IS IDENTICAL TO ACTIVATE AND DEACTIVATE. THE FAMILY IS NOT:
        Three families sharing one claim shape is a fair thing to be suspicious
        of, so here is the difference stated plainly. What a family expresses is
        not only what it CLAIMS but what it WRITES at commit, and these three
        write three different things to the same row:

            configure  -> conditions land; state becomes CONFIGURED unless the
                          subsystem is already running, in which case it stays
                          ACTIVE
            activate   -> state becomes ACTIVE; the subsystem starts emitting
            deactivate -> state becomes INACTIVE; conditions are retained as
                          last-known

        Merging them into one parameterised family would mean passing the
        target state through metadata, which puts a lifecycle decision in a
        caller-controlled dict rather than in the closed vocabulary. The whole
        reason `TransactionType` is closed is to keep that decision reviewable.

    WHY EXCLUSIVE, when configuring does not run anything:
        Because everything else reads what it writes. Two concurrent configures
        of one subsystem would both admit under a shared mode and the row would
        take whichever landed last, with no ordering anyone could reason about.
        More importantly, EXCLUSIVE is what makes configure and activate mutually
        excluding: recording conditions halfway through an activation would
        publish settings for a subsystem that is between states.

    THE ONE READ-BEFORE-WRITE IN THE PLANE, and why it is safe here:
        `record_conditions` preserves an ACTIVE state rather than overwriting
        it, which means it reads the current state and then writes. That is a
        race in general. It is not one here, for two specific reasons, and both
        must hold: the read and the write happen inside ONE registry lock
        acquisition, and this family holds `subsystem:<name>` EXCLUSIVE for the
        whole transaction, so no other lifecycle edge for this subsystem can be
        in flight. Remove either and the preservation rule becomes a coin flip.

    WHAT THIS DOES NOT DO:
        It does not push configuration INTO the subsystem. The plane cannot -
        it is forbidden to import one. This records what a subsystem SAYS about
        itself at a moment when nothing else can be writing that row. Whether
        the subsystem then honours what it announced is the subsystem's problem
        and is not observable from here.

    Threading:
        Stateless. Every hook is static or class level; safe to dispatch from
        any thread.

    Lifecycle / Cleanup:
        NEVER INSTANTIATED. Registered as a class; no instance state, no
        `Cleanable` surface.

    Registration:
        MELDER KERNEL - guarded. Registered against
        `TransactionType.SUBSYSTEM_CONFIGURE`; never bound.

    Subsystem Context:
        The first of the three subsystem lifecycle families in the usual order
        - configure, activate, deactivate - though none of the three requires
        another. A subsystem may activate without ever configuring; it simply has
        no conditions to report.

    System Context:
        All three subsystem roots now take `activate(configuration=None)`, and
        all three document the optional argument the same way: passing one is a
        convenience that CONFIGURES FIRST. So the two-step this family names
        already exists down there - it is simply not separately admissible,
        which is what this family adds.

        The plane still does not model HOW each subsystem arrives at the edge,
        and must not: it isolates the declaration. That restraint is what let
        Nexus be reworked from `enable`/`disable` to `activate`/`deactivate`
        without this family needing to know.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Claims one subsystem exclusively while recording the
        conditions it would run under, without switching it on. Melder kernel
        machinery: read it to understand the runtime, do not drive it directly.
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
            treated as ABSENT and degrades to the larger claim, matching every
            other family here - planning is not payload validation.

        Args:
            submitter:
                The identity originating the transaction.
            metadata:
                Caller-supplied inputs. `subsystem_name` selects the subsystem.

        Returns:
            Dict[str, ClaimMode]:
                `{world: INTENT, subsystem:<name>: EXCLUSIVE}` when the
                subsystem is known; otherwise `{world: EXCLUSIVE}`.
        """
        del submitter
        subsystem_name = metadata.get(
            SubsystemConfigureTransactionStrategy.METADATA_SUBSYSTEM_NAME
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
        Record the subsystem's declared conditions without switching it on.

        Contract:
            - Runs at commit WHILE CLAIMS ARE STILL HELD, so the conditions
              land atomically with the transaction that declared them.
            - Calls the base delta FIRST so the fact baseline is stamped, then
              records the conditions.
            - Reads ONLY the keys `ParticipationConditions` declares. A
              subsystem cannot widen its own row by adding metadata keys, and
              the bound lives in the vocabulary rather than being restated by
              each family that writes conditions.
            - Does NOT move an already-ACTIVE subsystem. That rule is enforced
              by `record_conditions`, not here, so there is one place to be
              right about it rather than one per caller.
            - A configure whose subject is unknown took `world` EXCLUSIVE and
              is a caller error, but refusing it is admission's job, not this
              hook's. Nothing is recorded, which leaves the store honest.
            - Failures PROPAGATE and poison the commit, per the base contract.
              Conditions that silently failed to write would leave a reader
              acting on the previous configuration while believing it had the
              new one.

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
        information_registry.record_conditions(
            subsystem_name=subsystem_name,
            conditions=ParticipationConditions.select(staged.metadata),
            reporter=staged.request_id,
        )
