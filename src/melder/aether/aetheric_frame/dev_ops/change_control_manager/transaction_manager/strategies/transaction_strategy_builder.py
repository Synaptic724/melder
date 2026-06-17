"""
Transaction-strategy registry for live change-control resolution.

This module does one job: own the mapping from transaction kind to strategy
class so `TransactionMediator` can ask one object, "given this transaction
type, which strategy class should resolve it?".

Why this exists
---------------
The mediator should not carry per-transaction policy branches inline. Once the
runtime has more than one meaningful transaction family, the transaction-kind
to strategy-class mapping needs one explicit owner. This builder is that owner.

What this file is responsible for
---------------------------------
- store the strategy registry
- normalize transaction-type input
- resolve one registered strategy class
- provide a small convenience layer around the three strategy operations:
  - `build_start_plan(...)`
  - `on_start(...)`
  - `on_end(...)`

What this file is not responsible for
-------------------------------------
- it does not perform admission
- it does not open embargoes
- it does not commit or abort requests
- it does not own transaction policy itself

Those responsibilities stay in the mediator and change-control layers. This
builder is only the registry and dispatch seam for strategy classes.
"""

from typing import TYPE_CHECKING, Dict, Type, Union

from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.bind_transaction_strategy import (
    BindTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.cluster_link_transaction_strategy import (
    ClusterLinkTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.link_transaction_strategy import (
    LinkTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.transfer_ownership_transaction_strategy import (
    TransferOwnershipTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.unlink_transaction_strategy import (
    UnlinkTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.notch_transaction_strategy import (
    NotchTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.add_to_index_transaction_strategy import (
    AddToIndexTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.remove_from_index_transaction_strategy import (
    RemoveFromIndexTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.elect_conduit_cluster_leader_transaction_strategy import (
    ElectConduitClusterLeaderTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.unelect_conduit_cluster_leader_transaction_strategy import (
    UnelectConduitClusterLeaderTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.transaction_strategy import (
    TransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)
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

class TransactionStrategyBuilder:
    """
    Registry-backed resolver for transaction strategies.

    Purpose:
        Centralize transaction-kind to strategy-class resolution in
        change-control land so callers only submit:
        - `transaction_type`
        - `DevopsIdentity`
        - `metadata`

        and do not carry strategy-selection logic themselves.

    Contract:
        - Owns one internal strategy registry keyed by normalized transaction
          name.
        - Registers the built-in strategy set during initialization.
        - Accepts either `ChangeTransactionType` or plain string transaction
          identifiers.
        - Uses the same builder-owned collaborators for every resolved
          strategy:
          - `ChangeControlTransactionManager`
          - `DevopsInformationRegistry`

    Threading:
        - The builder stores only immutable references plus a strategy map that
          is populated during initialization.
        - It is read-only during normal runtime use and does not require its
          own lock.
    """

    __slots__ = [
        "_transaction_manager",
        "_devops_information_registry",
        "_strategies_by_transaction_name",
    ]

    def __init__(
            self,
            transaction_manager: "ChangeControlTransactionManager",
            devops_information_registry: DevopsInformationRegistry,
    ) -> None:
        """
        Initialize one strategy registry over the live change-control surfaces.

        Args:
            transaction_manager:
                Frame-local transaction manager whose scope helpers and request
                utilities will be shared by registered strategies.
            devops_information_registry:
                Frame-local topology and transaction mirror used by registered
                strategies for object and relationship resolution.

        Contract:
            - Starts with an empty registry map.
            - Immediately registers the built-in strategy set through
              `_register_default_strategies()`.
            - Does not instantiate strategy objects; the registry stores
              strategy classes directly.
        """
        self._transaction_manager: ChangeControlTransactionManager = (
            transaction_manager
        )
        self._devops_information_registry: DevopsInformationRegistry = (
            devops_information_registry
        )
        self._strategies_by_transaction_name: Dict[str, Type[TransactionStrategy]] = {}
        self._register_default_strategies()

    def register_strategy(
            self,
            transaction_type: Union[ChangeTransactionType, str],
            strategy_class: Type[TransactionStrategy],
    ) -> None:
        """
        Register one strategy class for a transaction kind.

        Args:
            transaction_type:
                Transaction kind to normalize and use as the registry key.
            strategy_class:
                Strategy class implementing the `TransactionStrategyClass`
                contract.

        Contract:
            - Later registrations for the same normalized transaction name
              replace earlier ones.
            - Registration stores the class directly; no instance lifecycle is
              introduced here.
        """
        transaction_name = self._normalize_transaction_name(transaction_type)
        self._strategies_by_transaction_name[transaction_name] = strategy_class

    def resolve(
            self,
            transaction_type: Union[ChangeTransactionType, str],
    ) -> Type[TransactionStrategy]:
        """
        Resolve the registered strategy class for one transaction kind.

        Args:
            transaction_type:
                Transaction kind expressed as either enum or normalized string.

        Returns:
            Type[TransactionStrategyClass]:
                Registered strategy class for the supplied transaction kind.

        Raises:
            NotImplementedError:
                If no strategy class has been registered for the supplied
                transaction kind.
        """
        transaction_name = self._normalize_transaction_name(transaction_type)
        strategy_class = self._strategies_by_transaction_name.get(
            transaction_name
        )
        if strategy_class is None:
            raise NotImplementedError(
                f"Transaction strategy is not implemented for '{transaction_name}'."
            )
        return strategy_class

    def build_start_plan(
            self,
            *,
            transaction_type: Union[ChangeTransactionType, str],
            identity: DevopsIdentity,
            metadata: Dict[str, object],
    ) -> Dict[str, object]:
        """
        Build the start plan for one transaction request.

        Purpose:
            Give callers one registry-backed entrypoint for the pure strategy
            resolution step without exposing the strategy registry details.

        Args:
            transaction_type:
                Transaction kind to resolve.
            identity:
                Submitter identity entering the transaction system.
            metadata:
                Caller-supplied metadata for strategy resolution.

        Returns:
            Dict[str, object]:
                Strategy-produced normalized request inputs for mediator
                admission.
        """
        strategy_class = self.resolve(transaction_type)
        return strategy_class.build_start_plan(
            transaction_manager=self._transaction_manager,
            devops_information_registry=self._devops_information_registry,
            identity=identity,
            metadata=metadata,
        )

    def on_start(
            self,
            *,
            transaction_type: Union[ChangeTransactionType, str],
            identity: DevopsIdentity,
            metadata: Dict[str, object],
    ) -> None:
        """
        Run strategy-owned start side effects for one transaction kind.

        Purpose:
            Keep the mediator from needing to know which concrete strategy
            class owns the transaction's start-side local consequences.
        """
        strategy_class = self.resolve(transaction_type)
        strategy_class.on_start(
            devops_information_registry=self._devops_information_registry,
            identity=identity,
            metadata=metadata,
        )

    def on_end(
            self,
            *,
            transaction_type: Union[ChangeTransactionType, str],
            identity: DevopsIdentity,
            metadata: Dict[str, object],
    ) -> None:
        """
        Run strategy-owned end side effects for one transaction kind.

        Purpose:
            Keep the mediator from needing to know which concrete strategy
            class owns the transaction's end-side local consequences.
        """
        strategy_class = self.resolve(transaction_type)
        strategy_class.on_end(
            devops_information_registry=self._devops_information_registry,
            identity=identity,
            metadata=metadata,
        )

    def apply_commit_delta(
            self,
            *,
            transaction_type: Union[ChangeTransactionType, str],
            identity: DevopsIdentity,
            staged: "ChangeControlStagedMutation",
    ) -> None:
        """
        Apply the registered family's registry commit delta.

        Purpose:
            Give the mediator one registry-backed dispatch point for
            commit-time registry maintenance without exposing strategy
            selection details.

        Contract:
            - No-ops when this builder holds no registry reference.
            - Delegates to the resolved strategy class, which decides what
              (if anything) to write; the base default stamps fact records.

        Args:
            transaction_type:
                Transaction kind to resolve.
            identity:
                Submitter identity that originated the transaction.
            staged:
                Immutable staged mutation for the committing request.

        Returns:
            None.
        """
        if self._devops_information_registry is None:
            return
        strategy_class = self.resolve(transaction_type)
        strategy_class.apply_commit_delta(
            devops_information_registry=self._devops_information_registry,
            identity=identity,
            staged=staged,
        )

    def _register_default_strategies(self) -> None:
        """
        Register the built-in strategy set for this builder instance.

        Contract:
            - Bind-family requests are registered under the `bind` transaction
              name.
            - Link requests are registered under the `link` transaction name.
            - Cluster-owned share/unshare requests are registered under the
              `cluster_link` transaction name.
            - Ownership-transfer requests are registered under the
              `transfer_ownership` transaction name.
            - Conduit-owned unlink (sever-link) requests are registered under
              the `unlink` transaction name.
            - Additional strategy classes should be registered here as they
              become real runtime surfaces.
        """
        self.register_strategy(ChangeTransactionType.BIND, BindTransactionStrategy)
        self.register_strategy(ChangeTransactionType.LINK, LinkTransactionStrategy)
        self.register_strategy(
            ChangeTransactionType.CLUSTER_LINK,
            ClusterLinkTransactionStrategy,
        )
        self.register_strategy(
            ChangeTransactionType.TRANSFER_OWNERSHIP,
            TransferOwnershipTransactionStrategy,
        )
        self.register_strategy(
            ChangeTransactionType.UNLINK,
            UnlinkTransactionStrategy,
        )
        self.register_strategy(
            ChangeTransactionType.NOTCH,
            NotchTransactionStrategy,
        )
        self.register_strategy(
            ChangeTransactionType.ADD_TO_INDEX,
            AddToIndexTransactionStrategy,
        )
        self.register_strategy(
            ChangeTransactionType.REMOVE_FROM_INDEX,
            RemoveFromIndexTransactionStrategy,
        )
        self.register_strategy(
            ChangeTransactionType.ELECT_CONDUIT_CLUSTER_LEADER,
            ElectConduitClusterLeaderTransactionStrategy,
        )
        self.register_strategy(
            ChangeTransactionType.UNELECT_CONDUIT_CLUSTER_LEADER,
            UnelectConduitClusterLeaderTransactionStrategy,
        )

    @staticmethod
    def _normalize_transaction_name(
            transaction_type: Union[ChangeTransactionType, str],
    ) -> str:
        """
        Normalize one transaction kind into the registry key form.

        Args:
            transaction_type:
                Transaction kind supplied as enum or string.

        Returns:
            str:
                Lowercase normalized transaction name used by the strategy
                registry.

        Raises:
            TypeError:
                If `transaction_type` is neither a string nor a
                `ChangeTransactionType`.
            ValueError:
                If the normalized transaction name is empty.
        """
        if isinstance(transaction_type, ChangeTransactionType):
            value = transaction_type.value
        elif isinstance(transaction_type, str):
            value = transaction_type
        else:
            raise TypeError(
                "transaction_type must be a ChangeTransactionType or string."
            )
        normalized_value = value.strip().lower()
        if not normalized_value:
            raise ValueError("transaction_type must not be empty.")
        return normalized_value
