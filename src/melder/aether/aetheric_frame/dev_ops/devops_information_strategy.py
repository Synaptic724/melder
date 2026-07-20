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

    Threading:
        Stateless class-level family; `execute` is a static method with no
        per-strategy instance state to guard.

    Registration:
        MELDER KERNEL - guarded. Registered as CLASSES in a closed family; note
        for MRO auditors that guarding this base is safe because there is no
        seam through which a user supplies their own information strategy.

    Subsystem Context:
        The READ family of DevOps, deliberately separate from the transaction
        family that WRITES. `DevopsInformationStrategyBuilder` resolves these,
        and the concrete members render frame views, transaction activity,
        registry audits, transfer blast radius, and cluster fan-out.

    System Context:
        The separation stated in "Why this exists" is the architectural point:
        transaction strategies must not also own query logic. Entangling them
        would mean every new view risks perturbing admission, and every
        admission change risks breaking a view - two concerns that change for
        entirely different reasons and at very different rates.
        Returning a DETACHED payload is the second invariant, and it is what
        makes these strategies safe to expose to tooling and agents. A view
        that handed back live registry structures would let a consumer mutate
        control-plane state by accident, and would make the returned answer
        change underneath the reader while they walked it. Detachment means the
        answer is a snapshot the caller owns outright.
        Receiving the LIVE registry while returning detached results is
        therefore not a contradiction: the strategy reads current truth at
        execution time precisely so the snapshot it produces is current.
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
