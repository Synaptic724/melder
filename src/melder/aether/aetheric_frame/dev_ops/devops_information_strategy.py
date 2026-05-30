from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
        DevopsInformationRegistry,
    )


class DevopsInformationStrategy(ABC):
    """
    Abstract base for DevOps information strategies.

    Purpose:
        Define the smallest explicit contract for strategy classes that consume
        the mirrored DevOps information state owned by
        `DevopsInformationRegistry`.

    Why this exists:
        Transaction strategies should not also own registry-maintenance or
        information-query logic. This abstraction provides the separate strategy
        family that can later manage registry updates and build registry-backed
        results without coupling those behaviors to the transaction layer.

    Contract:
        - Strategies are registered as classes, not long-lived instances.
        - Each strategy receives the live `DevopsInformationRegistry`.
        - Each strategy receives caller-supplied metadata.
        - Each strategy returns one detached result payload.
    """

    @staticmethod
    @abstractmethod
    def execute(
            *,
            devops_information_registry: "DevopsInformationRegistry",
            metadata: Dict[str, object],
    ) -> Dict[str, object]:
        """
        Execute one registry-backed information strategy.

        Args:
            devops_information_registry:
                Live mirrored DevOps registry to consume.
            metadata:
                Caller-supplied metadata for strategy resolution.

        Returns:
            Dict[str, object]:
                Detached strategy result payload.
        """
        raise NotImplementedError
