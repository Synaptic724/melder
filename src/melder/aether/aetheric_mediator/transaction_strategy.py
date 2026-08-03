"""
The dispatch contract every plane transaction family implements.

Dependency-free beyond the standard library.

Mirrors `TransactionStrategy` in the DevOps plane, including the property that
makes the whole design worth having: `build_start_plan` is where SCOPE
PROPORTIONALITY is decided. A family that over-claims turns the plane into a
global mutex with extra steps; a family that under-claims loses isolation.
Everything else here is lifecycle plumbing around that one judgement.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Mapping

from melder.aether.aetheric_mediator.claim_mode import ClaimMode
from melder.aether.aetheric_mediator.identity import Identity

if TYPE_CHECKING:
    from melder.aether.aetheric_mediator.information_registry import (
        InformationRegistry,
    )
    from melder.aether.aetheric_mediator.staged_transaction import (
        StagedTransaction,
    )


class TransactionStrategy(ABC):
    """
    Abstract base for one plane transaction family.

    Purpose:
        Define what a transaction of a given type CLAIMS, and what local work
        it performs at start, end, and commit.

    Why ABC and not Protocol:
        This is a closed, registered family with an explicit runtime
        inheritance contract and several concrete implementations dispatched
        polymorphically - the repo's sanctioned ABC case. `Protocol` is for
        genuine structural typing, which this is not.

    Contract:
        - REGISTERED AS CLASSES, NOT INSTANCES. Every hook is static or class
          level, so there is no per-strategy instance state to guard.
          Concurrency lives entirely in the mediator and the claims it holds.
        - `build_start_plan` is PURE. It reads identity and metadata and
          returns a claim map. It must not mutate anything, because it runs
          BEFORE admission and may be discarded if admission refuses.
        - `on_start` runs AFTER admission succeeds, with claims held.
        - `on_end` runs during finalisation, on both the commit and abort
          paths, so it must be safe when the transaction failed.
        - `apply_commit_delta` runs at commit WHILE CLAIMS ARE STILL HELD.
          That is the invariant that makes any registry write it performs
          race-free against overlapping writers. The base implementation
          stamps fact-record baselines and is usually sufficient; override it
          only when a family owns relational truth of its own.

    Scope proportionality - the judgement each family must get right:
        DevOps' bind family is the worked example. Pre-conjure a bind touches
        one spellbook; post-conjure it reaches the root conduit, its ward, and
        any cluster the root belongs to. It deliberately REFUSES to model bind
        as a multi-conduit fanout, because claiming every conduit associated
        with the book would serialise unrelated work across the whole frame
        for what is usually a single-surface operation. Every family here owes
        the same analysis: claim what the operation genuinely reaches, and no
        more.

    Lifecycle / Cleanup:
        NEVER INSTANTIATED, so there is nothing to clean and no `Cleanable`
        contract. Strategies are REGISTERED AS CLASSES and every hook is
        static or class level - `StrategyBuilder` stores the type object
        itself and dispatches on it. A strategy with instance state would need
        a lifecycle; the contract deliberately forbids having any.

    Threading:
        Stateless. Safe to dispatch from any thread.

    Registration:
        MELDER KERNEL - guarded. Registered by the plane; never bound.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Dispatch contract for one transaction family.
        build_start_plan decides scope proportionality; the rest is lifecycle.
    """

    @staticmethod
    @abstractmethod
    def build_start_plan(
            *,
            submitter: Identity,
            metadata: Mapping[str, Any],
    ) -> Dict[str, ClaimMode]:
        """
        Decide which scopes this transaction claims, and in which modes.

        Contract:
            PURE. No mutation, no side effects - this runs before admission
            and is discarded if admission refuses. The returned mapping is
            COMPLETE: every scope key carries an explicit mode, because this
            plane has no implicit default.

        Args:
            submitter: The identity originating the transaction.
            metadata: Caller-supplied inputs for the family.

        Returns:
            Dict[str, ClaimMode]: The complete scope-claim set.
        """
        raise NotImplementedError

    @staticmethod
    def on_start(
            *,
            submitter: Identity,
            staged: "StagedTransaction",
    ) -> None:
        """
        Run family-local work after admission succeeds.

        Contract:
            Claims are HELD when this runs.

            DEFAULTS TO NOTHING, and is deliberately NOT abstract. Most families
            have no runtime work to do here: in the DevOps plane only `notch`
            and the cluster-leader pair quiesce gates, and the other thirteen
            return immediately. Forcing every family to write an empty override
            buries the two that matter in eleven that do not, and makes the
            presence of an override carry no information.

            With a default, AN OVERRIDE MEANS SOMETHING. If you see one, this
            family freezes or prepares real state and you should read it.

            `build_start_plan` stays abstract for the opposite reason: there is
            no defensible default claim set. A guessed one is exactly how
            isolation is lost quietly.

        Args:
            submitter: The identity originating the transaction.
            staged: The immutable post-admission record.

        Returns:
            None.
        """
        del submitter
        del staged

    @staticmethod
    def on_end(
            *,
            submitter: Identity,
            staged: "StagedTransaction",
    ) -> None:
        """
        Run family-local work during finalisation.

        Contract:
            Runs on BOTH the commit and the failure path, so it must be safe
            when the transaction did not succeed. Anything that should happen
            only on success belongs in `apply_commit_delta`.

            DEFAULTS TO NOTHING, for the reason given on `on_start`. A family
            that overrode `on_start` to freeze something almost always overrides
            this to release it - that pairing is the signal, and it is invisible
            when every family implements both as no-ops.

        Args:
            submitter: The identity originating the transaction.
            staged: The immutable post-admission record.

        Returns:
            None.
        """
        del submitter
        del staged

    @classmethod
    def apply_commit_delta(
            cls,
            *,
            information_registry: "InformationRegistry",
            submitter: Identity,
            staged: "StagedTransaction",
    ) -> None:
        """
        Apply this family's registry delta for one committing transaction.

        Contract:
            - Runs at commit WHILE CLAIMS ARE STILL HELD, so writes are
              race-free against overlapping writers by construction.
            - The DEFAULT stamps a fact-record baseline for every region the
              staged transaction names. That baseline is what lets reporting
              skip re-derivation when nothing has changed since.
            - Failures PROPAGATE and poison the commit, exactly like a commit
              hook failure. A delta that silently failed would leave reporting
              claiming freshness it does not have.

        Args:
            information_registry: The plane registry to stamp.
            submitter: The identity originating the transaction.
            staged: The immutable post-admission record.

        Returns:
            None.
        """
        for region in staged.regions():
            information_registry.report_fact(
                fact_family=staged.transaction_type.value,
                region=region,
                reporter=staged.request_id,
            )
