"""
The graft family: the lane that takes no authority at all today.

Dependency-free beyond the standard library and this package.

`TransactionType`'s provenance note is blunt about this one - the `GraftRunner`
lane is "explicitly user-verb activity that takes NO load authority today". The
subsystem survey confirmed it from source: a graft of N members is N independent
per-verb transactions, nothing prevents a structural mutation interleaving
between member 3 and member 4, and nothing rolls back members 1-3 if member 4
refuses. This family is the first admission this lane has ever had.
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


class IndexGraftTransactionStrategy(TransactionStrategy):
    """
    Mark one frame as under piece-work for the duration of a graft.

    Purpose:
        Give the graft lane an admission claim proportionate to what this plane
        is permitted to isolate, without pretending to isolate what it is not.

    Contract:
        - When metadata carries a non-empty string `host_frame_name`, claims
          `world` INTENT plus `frame:<host_frame_name>` INTENT.
        - Otherwise claims `world` EXCLUSIVE, on the same unknown-reach reasoning
          the formation-load family uses.
        - PURE. Reads metadata, mutates nothing.

    WHY BOTH CLAIMS ARE INTENT, AND WHY THAT IS THE HONEST MODE:
        A graft does not own the frame it works in. It binds members into ONE
        host book and may notch ONE index; the rest of the frame is untouched and
        another graft into a different book has no reason to wait. `frame:` at
        EXCLUSIVE would serialise every graft in a frame against every other,
        which is the over-claim the `TransactionStrategy` contract warns about -
        a plane that turns into a global mutex with extra steps.

        `ix` says precisely what is true: piece-work is happening inside this
        frame. It coexists with other `ix` holders, so parallel grafts proceed.
        It excludes an `x` holder, so a formation load into that frame and a
        checkpoint load over the world are both correctly blocked - and those are
        exactly the two operations that would corrupt a graft in flight.

    WHAT THIS DELIBERATELY DOES NOT CLAIM, and the gap it leaves:
        Not `spellbook:<host_book_id>`, not `conduit:<id>`, not
        `spell_index:<id>` - all three are inside a frame and belong to that
        frame's own `ChangeControlManager`. The survey that produced this family
        identified all three as the real mutation targets, and this plane still
        must not name them.

        STATE THE CONSEQUENCE PLAINLY: two grafts into the SAME host book will
        both admit here, because both hold only `ix` on the same frame. This
        family does not make the graft lane safe on its own. It makes the graft
        VISIBLE to the plane and blocks the whole-frame and whole-world
        operations that would destroy it; isolating book-level overlap remains
        the frame plane's job, and the graft lane does not currently ask it for
        that either. The survey records that as an open gap in the subsystem, not
        something this family can close from above.

    Threading:
        Stateless. Every hook is static; safe to dispatch from any thread.

    Lifecycle / Cleanup:
        NEVER INSTANTIATED. Registered as a class; no instance state, no
        `Cleanable` surface.

    Registration:
        MELDER KERNEL - guarded. Registered against `TransactionType.INDEX_GRAFT`;
        never bound.

    Subsystem Context:
        The only family here whose subsystem verb takes NO authority today, which
        makes it the one where adding the plane changes live behaviour rather
        than restating an existing law in new vocabulary.

    System Context:
        The graft lane runs each member through ordinary public bind /
        bind_inactive / notch verbs, each of which opens its own frame-level
        transaction. Holding `frame:` INTENT here nests correctly with that: the
        outer claim marks the frame busy, the inner per-verb transactions claim
        the book and index beneath it. That nesting is the intended composition
        between the two planes.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Marks one frame as under piece-work for a graft, using
        intent rather than exclusive so parallel grafts coexist. Melder kernel
        machinery: read it to understand the runtime, do not drive it directly.
    """

    METADATA_HOST_FRAME_NAME = "host_frame_name"

    @staticmethod
    def build_start_plan(
            *,
            submitter: Identity,
            metadata: Mapping[str, Any],
    ) -> dict[str, ClaimMode]:
        """
        Return the frame-intent claim set, or the whole-world set when unknown.

        Contract:
            PURE. A `host_frame_name` present but not a non-empty string is
            treated as ABSENT and degrades to the larger claim, matching the
            formation-load family - planning is not payload validation.

        Args:
            submitter:
                The identity originating the transaction.
            metadata:
                Caller-supplied inputs. `host_frame_name` selects the frame.

        Returns:
            Dict[str, ClaimMode]:
                `{world: INTENT, frame:<name>: INTENT}` when the host frame is
                known; otherwise `{world: EXCLUSIVE}`.
        """
        del submitter
        host_frame_name = metadata.get(
            IndexGraftTransactionStrategy.METADATA_HOST_FRAME_NAME
        )
        if not isinstance(host_frame_name, str) or not host_frame_name:
            return {ScopeKey.world(): ClaimMode.EXCLUSIVE}
        return {
            ScopeKey.world(): ClaimMode.INTENT,
            ScopeKey.frame(host_frame_name): ClaimMode.INTENT,
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
            No family-local work; the graft is performed by the claim holder.

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
