"""
The frame-scoped load family: the primary case for parallelism on this plane.

Dependency-free beyond the standard library and this package.

`TransactionType`'s own provenance note names this family as the reason frame
scope exists: formations are SINGLE-FRAME by law ("multi-frame windows refuse"),
so two formation loads into two different frames have no structural reason to
serialise. This is where the plane earns its keep over a global gate.
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


class FormationLoadTransactionStrategy(TransactionStrategy):
    """
    Claim one frame for a formation restore, or the world when the frame is unknown.

    Purpose:
        Isolate a single-frame restore to that frame, so disjoint restores run
        together, while still excluding any whole-world operation.

    Contract:
        - When metadata carries a non-empty string `target_frame_name`, claims
          `world` INTENT plus `frame:<target_frame_name>` EXCLUSIVE.
        - Otherwise claims `world` EXCLUSIVE - see "The fallback is not laziness"
          below, because this branch is the important one.
        - PURE. Reads metadata, mutates nothing.

    The parent/child pair, and why `world` is INTENT rather than absent:
        `ix` on `world` is the HIERARCHICAL PARENT-SCOPE MARKER: it declares
        "piece-work is happening beneath this scope". Two formation loads into
        different frames both hold `world` INTENT, which coexists, and each holds
        its own `frame:` key EXCLUSIVE, which does not overlap - so they proceed
        in parallel. A checkpoint load asking for `world` EXCLUSIVE is excluded by
        either of them, which is exactly right: a whole-world rebuild must not
        run while a frame is being restored underneath it.

        Omitting the `world` claim entirely would break that. Two claims that
        never meet cannot arbitrate, and the world-level operation would admit
        straight through a live frame restore.

    The fallback is not laziness:
        A formation record whose target frame cannot be determined before
        admission has UNKNOWN REACH. The honest claim for unknown reach is the
        largest one, because admission happens BEFORE the record is opened and
        the plan cannot be revised afterwards - `build_start_plan` is pure and
        runs once. Claiming a guessed frame and being wrong would isolate the
        wrong surface and admit a genuine conflict, which is worse than being
        briefly coarse. The caller controls this: supply `target_frame_name` and
        get parallelism; omit it and get correctness.

    Scope proportionality:
        This family deliberately does NOT enumerate what inside the frame the
        restore touches - books, conduits, indexes, contracts. Those live inside
        the frame and belong to the frame's own admission authority. See the
        package docstring on jurisdiction.

    Threading:
        Stateless. Every hook is static; safe to dispatch from any thread.

    Lifecycle / Cleanup:
        NEVER INSTANTIATED. Registered as a class; no instance state, no
        `Cleanable` surface.

    Registration:
        MELDER KERNEL - guarded. Registered against
        `TransactionType.FORMATION_LOAD`; never bound.

    Subsystem Context:
        The frame-scoped counterpart to `CheckpointLoadTransactionStrategy`. Same
        subsystem, same verb family, different claim shape - because one rebuilds
        the world and the other rebuilds one frame.

    System Context:
        The scoped-restore lane can RETARGET onto a frame other than the recorded
        one. The claim must follow the TARGET, not the recorded origin, because
        the target is the frame that gets written. `target_frame_name` in metadata
        is therefore the retarget value when one was supplied, not the record's
        own frame.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Claims one frame exclusively under a world intent
        marker, falling back to whole-world exclusivity when the target frame is
        not known before admission. Melder kernel machinery: read it to
        understand the runtime, do not drive it directly.
    """

    METADATA_TARGET_FRAME_NAME = "target_frame_name"

    @staticmethod
    def build_start_plan(
            *,
            submitter: Identity,
            metadata: Mapping[str, Any],
    ) -> Dict[str, ClaimMode]:
        """
        Return the frame-scoped claim set, or the whole-world set when unknown.

        Contract:
            PURE. A `target_frame_name` that is present but not a non-empty
            string is treated as ABSENT rather than raising: admission planning
            is not the place to validate a caller's payload, and degrading to the
            larger claim is safe where refusing would turn a metadata typo into a
            failed restore.

        Args:
            submitter:
                The identity originating the transaction.
            metadata:
                Caller-supplied inputs. `target_frame_name` selects the frame.

        Returns:
            Dict[str, ClaimMode]:
                `{world: INTENT, frame:<name>: EXCLUSIVE}` when the target frame
                is known; otherwise `{world: EXCLUSIVE}`.
        """
        del submitter
        target_frame_name = metadata.get(
            FormationLoadTransactionStrategy.METADATA_TARGET_FRAME_NAME
        )
        if not isinstance(target_frame_name, str) or not target_frame_name:
            return {ScopeKey.world(): ClaimMode.EXCLUSIVE}
        return {
            ScopeKey.world(): ClaimMode.INTENT,
            ScopeKey.frame(target_frame_name): ClaimMode.EXCLUSIVE,
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
            No family-local work; the restore is performed by the claim holder.

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
