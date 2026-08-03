"""
The founding family: admitting the creation of a frame.

Dependency-free beyond the standard library and this package.

This is the transaction the whole plane exists for. `AethericFrame` creation
could not be admitted by anything that existed before: the only admission
authority was the frame-local `TransactionMediator`, and that object is owned BY
the frame being created. An authority cannot arbitrate its own construction.

The consequence was measurable rather than theoretical. `Aether._ensure_frame`
is reached from SIX call sites across four subsystems - `Spellbook.__init__`
(a book births the frame it names), the crystallizer restore engine, the Nexus
frame-descriptor and frame managers, and Aether's own default-frame path - and
none of them coordinated with any of the others.
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


class FrameCreateTransactionStrategy(TransactionStrategy):
    """
    Claim one frame exclusively while it is brought into existence.

    Purpose:
        Give frame creation the admission it has never had, so a frame cannot be
        born underneath an operation that believes it holds the world.

    Contract:
        - When metadata carries a non-empty string `frame_name`, claims
          `world` INTENT plus `frame:<frame_name>` EXCLUSIVE.
        - Otherwise claims `world` EXCLUSIVE, on the same unknown-reach
          reasoning every other family here uses.
        - PURE. Reads metadata, mutates nothing.

    WHAT THIS ACTUALLY BUYS, stated concretely because "isolation" is too vague
    to check:
        A checkpoint load holds `world` EXCLUSIVE for the length of its replay.
        Before this family existed, a `Spellbook` constructed on another thread
        would call `_ensure_frame` and birth a frame straight through that
        replay - the load would rebuild a world that grew a frame while it was
        being rebuilt. Now the frame-create claim is excluded by the load's
        world claim and the constructing thread waits, which is the behaviour
        every reader already assumed was there.

        The converse holds too: a frame being created excludes a checkpoint load
        from starting, because `world` INTENT and `world` EXCLUSIVE do not
        coexist.

    Why `frame:<name>` EXCLUSIVE and not INTENT:
        Creating a frame is a whole-unit write on that frame - it does not
        exist, then it does. There is no piece-work beneath it for a peer to do
        concurrently. Two threads racing to create the SAME frame is not
        parallelism, it is the race this family is here to arbitrate, and
        EXCLUSIVE turns it into one winner and one waiter.

        Two threads creating DIFFERENT frames still proceed together, because
        their child keys are disjoint. That is the whole reason the parent
        marker is INTENT rather than EXCLUSIVE.

    WHAT THIS DOES NOT COVER, and it is the honest half:
        The epic's founding complaint is that `_ensure_frame(...)` followed by
        `bind_frame_configuration(...)` cannot be made atomic - two calls, two
        different locks. This family admits the CREATION. It does not, by
        itself, span the posture call that follows, because that is the
        caller's span rather than Aether's. A caller that needs the pair to be
        atomic must hold ONE session across both, which is possible now and was
        not before. Claiming otherwise would overstate what a claim on creation
        delivers.

    Threading:
        Stateless. Every hook is static; safe to dispatch from any thread.

    Lifecycle / Cleanup:
        NEVER INSTANTIATED. Registered as a class; no instance state, no
        `Cleanable` surface.

    Registration:
        MELDER KERNEL - guarded. Registered against
        `TransactionType.FRAME_CREATE`; never bound.

    Subsystem Context:
        Sits directly beneath `world` alongside the load families, and directly
        above every frame-local `ChangeControlManager` - which cannot exist
        until this transaction has completed.

    System Context:
        RE-ENTRANCY IS THE HAZARD HERE, not contention. `_ensure_frame` is
        called from inside operations that already hold plane claims - the
        restore engine calls it mid-replay while its load holds `world`. A
        second root session for the same work would block on the claim its own
        caller is holding, which is a self-deadlock rather than a refusal.
        Aether therefore opens this transaction ONLY when the calling thread is
        not already inside a plane session; when it is, the outer transaction
        has already claimed what this work touches.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Claims one frame exclusively under a world intent
        marker while the frame is created. Melder kernel machinery: read it to
        understand the runtime, do not drive it directly.
    """

    METADATA_FRAME_NAME = "frame_name"

    @staticmethod
    def build_start_plan(
            *,
            submitter: Identity,
            metadata: Mapping[str, Any],
    ) -> dict[str, ClaimMode]:
        """
        Return the frame-scoped claim set, or the whole-world set when unknown.

        Contract:
            PURE. A `frame_name` present but not a non-empty string is treated
            as ABSENT and degrades to the larger claim, matching every other
            family here - planning is not payload validation.

        Args:
            submitter:
                The identity originating the transaction.
            metadata:
                Caller-supplied inputs. `frame_name` selects the frame.

        Returns:
            Dict[str, ClaimMode]:
                `{world: INTENT, frame:<name>: EXCLUSIVE}` when the frame name
                is known; otherwise `{world: EXCLUSIVE}`.
        """
        del submitter
        frame_name = metadata.get(
            FrameCreateTransactionStrategy.METADATA_FRAME_NAME
        )
        if not isinstance(frame_name, str) or not frame_name:
            return {ScopeKey.world(): ClaimMode.EXCLUSIVE}
        return {
            ScopeKey.world(): ClaimMode.INTENT,
            ScopeKey.frame(frame_name): ClaimMode.EXCLUSIVE,
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
            No family-local work. Aether constructs the frame while holding the
            claim; a strategy that built it would be the plane reaching into the
            runtime it is forbidden to import.

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
