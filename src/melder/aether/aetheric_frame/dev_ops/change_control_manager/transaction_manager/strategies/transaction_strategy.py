from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, Optional

from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)
from melder.aether.aetheric_frame.dev_ops.devops_identity import (
    DevopsIdentity,
)

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.orchestrator.staged_mutation import (
        ChangeControlStagedMutation,
    )
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
        ChangeControlTransactionManager,
    )


class TransactionStrategy(ABC):
    """
    Abstract base for transaction strategy classes.

    Purpose:
        Define the explicit runtime contract that every mediator-registered
        transaction strategy class must implement.

    Why this is an abstract base instead of a protocol
    --------------------------------------------------
    These strategies are not ad hoc structural collaborators. They are a
    deliberate runtime family of registered strategy classes with one shared
    dispatch contract owned by the transaction mediator/builder layer.

    Contract:
        - Strategies are registered as classes, not runtime instances.
        - `build_start_plan(...)` is the pure planning step that translates
          identity + metadata into normalized request inputs.
        - `on_start(...)` runs local strategy-owned start side effects after
          admission succeeds.
        - `on_end(...)` runs local strategy-owned end side effects during
          transaction finalization.
        - `apply_commit_delta(...)` applies the family's registry delta at
          commit time, while the transaction still holds its scope claims.
          The base class provides a fact-record-stamping default; families
          override it when they own relational registry truth.
        - Registered strategies must implement the three abstract methods.

    Threading:
        Stateless: strategies are registered as CLASSES and every hook is a
        static/class-level call, so there is no per-strategy instance state to
        guard. Concurrency lives in the mediator and the scope claims it holds.

    Registration:
        MELDER KERNEL - guarded. NOTE for MRO auditors: this is a guarded base
        with many subclasses, which is safe here because every registered
        strategy family ships with melder and the registry is closed - there is
        no seam through which a user supplies their own strategy class.

    Subsystem Context:
        The dispatch contract for the transaction family
        (`bind`, `link`, `unlink`, `cluster_link`, `cluster_join`,
        `cluster_leave`, `transfer_ownership`, `conjure`, `notch`,
        `add_to_index`, `remove_from_index`, and the cluster-leader pair).
        `TransactionStrategyBuilder` resolves the family, the mediator admits
        it, and the embargo table plus root session govern the claim window.

    System Context:
        The four-hook shape maps onto the transaction lifecycle deliberately,
        and `apply_commit_delta` is the one that carries the real invariant: it
        runs at commit WHILE THE TRANSACTION STILL HOLDS ITS SCOPE CLAIMS. That
        is what makes the link and cluster-membership mirrors maintainable
        eagerly at the mutation site and race-safe - so downstream information
        strategies need no relational commit deltas of their own and can trust
        the mirror they read.
        The ABC-over-Protocol choice stated above is applying the repo's own
        interface rule rather than a style preference: use `ABC` when there is
        an explicit runtime inheritance contract with multiple concrete
        implementations, and `Protocol` only for genuine structural typing.
        This family is registered, closed, and dispatched polymorphically -
        precisely the sanctioned ABC case.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Abstract base for transaction strategy classes. Melder kernel "
        "machinery: read it to understand the runtime, do not drive it directly."
    )

    @staticmethod
    @abstractmethod
    def build_start_plan(
            *,
            transaction_manager: "ChangeControlTransactionManager",
            devops_information_registry: DevopsInformationRegistry,
            identity: DevopsIdentity,
            metadata: Dict[str, object],
    ) -> Dict[str, object]:
        """
        Build normalized request inputs for one transaction start.

        Args:
            transaction_manager:
                Frame-local scope-key and request helper surface shared by
                transaction strategies.
            devops_information_registry:
                Frame-local topology registry used to resolve affected
                identities and object relationships.
            identity:
                Submitter identity entering the transaction system.
            metadata:
                Caller-supplied metadata for strategy resolution.

        Returns:
            Dict[str, object]:
                Normalized request inputs suitable for mediator admission.
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def on_start(
            *,
            devops_information_registry: DevopsInformationRegistry,
            identity: DevopsIdentity,
            metadata: Dict[str, object],
    ) -> None:
        """
        Run strategy-owned start side effects after admission succeeds.

        Args:
            devops_information_registry:
                Frame-local topology registry used to resolve live runtime
                objects needed for local start consequences.
            identity:
                Submitter identity that originated the transaction.
            metadata:
                Metadata associated with the resolved transaction start.

        Returns:
            None.
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def on_end(
            *,
            devops_information_registry: DevopsInformationRegistry,
            identity: DevopsIdentity,
            metadata: Dict[str, object],
    ) -> None:
        """
        Run strategy-owned end side effects during transaction finalization.

        Args:
            devops_information_registry:
                Frame-local topology registry used to resolve live runtime
                objects needed for local end consequences.
            identity:
                Submitter identity that originated the transaction.
            metadata:
                Metadata associated with the resolved transaction start.

        Returns:
            None.
        """
        raise NotImplementedError

    @classmethod
    def apply_commit_delta(
            cls,
            *,
            devops_information_registry: Optional[DevopsInformationRegistry],
            identity: DevopsIdentity,
            staged: "ChangeControlStagedMutation",
    ) -> None:
        """
        Apply this family's registry delta for one committing transaction.

        Purpose:
            Make transactions the only maintainers of mirrored registry truth.
            The default implementation stamps last-reported fact records for
            every region the staged mutation names, establishing the baseline
            that lets information strategies skip re-derivation when all
            changes since the baseline flowed through the plane.

        Contract:
            - Runs while the transaction still holds its scope claims; deltas
              are race-free against overlapping writers by construction.
            - The default stamps fact records only; it performs no relational
              registry writes. Families override this method when their
              runtime callers supply unambiguous relational deltas (edge
              direction, share/unshare intent) in staged metadata.
            - No-ops when the registry is absent.
            - Failures propagate and poison the commit like commit-hook
              failures.

        Args:
            devops_information_registry:
                Frame-local registry to update, when present.
            identity:
                Submitter identity that originated the transaction.
            staged:
                Immutable staged mutation for the committing request.

        Returns:
            None.
        """
        if devops_information_registry is None:
            return
        fact_family = (
            staged.request_type.value
            if hasattr(staged.request_type, "value")
            else str(staged.request_type)
        )
        reporter = staged.request_id
        if staged.spellbook_id:
            devops_information_registry.report_fact(
                fact_family=fact_family,
                region=f"spellbook:{staged.spellbook_id}",
                reporter=reporter,
            )
        for conduit_id in staged.conduit_ids:
            if not conduit_id:
                continue
            devops_information_registry.report_fact(
                fact_family=fact_family,
                region=f"conduit:{conduit_id}",
                reporter=reporter,
            )
