from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict

from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)
from melder.aether.aetheric_frame.dev_ops.devops_identity import (
    DevopsIdentity,
)

if TYPE_CHECKING:
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
        - Registered strategies must implement all three methods.
    """

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
        """
        raise NotImplementedError
