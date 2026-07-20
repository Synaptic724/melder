from typing import TYPE_CHECKING, Dict, Tuple, Type

from melder.aether.aetheric_frame.dev_ops.devops_information_strategy import (
    DevopsInformationStrategy,
)
from melder.aether.aetheric_frame.dev_ops.information_strategies.cluster_fanout_strategy import (
    ClusterFanoutStrategy,
)
from melder.aether.aetheric_frame.dev_ops.information_strategies.frame_operational_view_strategy import (
    FrameOperationalViewStrategy,
)
from melder.aether.aetheric_frame.dev_ops.information_strategies.registry_consistency_audit_strategy import (
    RegistryConsistencyAuditStrategy,
)
from melder.aether.aetheric_frame.dev_ops.information_strategies.transaction_activity_view_strategy import (
    TransactionActivityViewStrategy,
)
from melder.aether.aetheric_frame.dev_ops.information_strategies.transfer_blast_radius_strategy import (
    TransferBlastRadiusStrategy,
)

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
        DevopsInformationRegistry,
    )


class DevopsInformationStrategyBuilder:
    """
    Registry-backed resolver for DevOps information strategies.

    Purpose:
        Centralize strategy-name to strategy-class resolution for the DevOps
        information layer so callers can ask the registry for one named
        information tool without carrying their own strategy maps.

    Contract:
        - Owns one internal strategy registry keyed by normalized strategy name.
        - Stores strategy classes directly; it does not own strategy instances.
        - Exposes registration, resolution, execution, and name-listing helpers.
        - Registers the default information-strategy catalog at construction;
          callers may register additional strategies on top.
        - Counts successful executions per normalized strategy name so the
          control plane can see which information checks actually run.
        - Does not mutate the registry by itself outside strategy execution.

    Owned State:
        The name-to-class strategy map and the per-name success counters.
        Strategy CLASSES, never instances.

    Threading:
        Registration and execution counting are serialized internally; the
        strategies themselves are stateless, so concurrent execution of the
        same named strategy is safe.

    Registration:
        MELDER KERNEL - guarded. Frame-owned resolver reached through the
        DevOps surface.

    Subsystem Context:
        The resolver for the information (READ) family, mirroring what
        `TransactionStrategyBuilder` does for the transaction (WRITE) family.
        Both exist so callers name a capability instead of importing and
        wiring strategy classes themselves.

    System Context:
        Registering a DEFAULT CATALOG at construction while still allowing
        additional registrations is what makes this an extension point rather
        than a fixed switch: the shipped information tools are available
        immediately, and a caller can add one without forking the resolver.
        The execution counters are the non-obvious feature and they answer an
        operational question that is otherwise invisible - WHICH information
        checks actually run. A strategy registered but never executed is dead
        weight, and one executing far more than expected is usually a caller
        re-deriving a view it could have cached against a
        `DevopsFactRecord` baseline. Counting only SUCCESSFUL executions keeps
        that signal honest, since failed attempts say nothing about which
        checks the system genuinely relies on.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Registry-backed resolver for DevOps information strategies. Melder "
        "kernel machinery: read it to understand the runtime, do not drive it directly."
    )

    __slots__ = [
        "_devops_information_registry",
        "_strategies_by_name",
        "_execution_counts_by_name",
    ]

    def __init__(
            self,
            devops_information_registry: "DevopsInformationRegistry",
    ) -> None:
        """
        Initialize one information-strategy builder over a live registry.

        Args:
            devops_information_registry:
                Live DevOps information registry that registered strategies will
                consume.

        Raises:
            ValueError:
                If the registry is None.

        Returns:
            None.
        """
        if devops_information_registry is None:
            raise ValueError("devops_information_registry must not be None.")
        self._devops_information_registry: DevopsInformationRegistry = (
            devops_information_registry
        )
        self._strategies_by_name: Dict[str, Type[DevopsInformationStrategy]] = {}
        self._execution_counts_by_name: Dict[str, int] = {}
        self._register_default_strategies()

    def _register_default_strategies(self) -> None:
        """
        Register the built-in information-strategy catalog.

        Contract:
            - Registers the five default strategies: transaction activity
              view, cluster fanout, transfer blast radius, frame operational
              view, and registry consistency audit.
            - Idempotent by construction order; later explicit registrations
              under the same names override the defaults.

        Returns:
            None.
        """
        self.register_strategy(
            "transaction_activity_view",
            TransactionActivityViewStrategy,
        )
        self.register_strategy("cluster_fanout", ClusterFanoutStrategy)
        self.register_strategy(
            "transfer_blast_radius",
            TransferBlastRadiusStrategy,
        )
        self.register_strategy(
            "frame_operational_view",
            FrameOperationalViewStrategy,
        )
        self.register_strategy(
            "registry_consistency_audit",
            RegistryConsistencyAuditStrategy,
        )

    def register_strategy(
            self,
            strategy_name: str,
            strategy_class: Type[DevopsInformationStrategy],
    ) -> None:
        """
        Register one strategy class under a normalized strategy name.

        Args:
            strategy_name:
                User-facing strategy key.
            strategy_class:
                Strategy class implementing `DevopsInformationStrategy`.

        Returns:
            None.
        """
        normalized_name = self._normalize_strategy_name(strategy_name)
        self._strategies_by_name[normalized_name] = strategy_class

    def resolve(self, strategy_name: str) -> Type[DevopsInformationStrategy]:
        """
        Resolve one registered strategy class by name.

        Args:
            strategy_name:
                Strategy key to resolve.

        Returns:
            Type[DevopsInformationStrategy]:
                Registered strategy class.

        Raises:
            NotImplementedError:
                If no strategy is registered for the supplied name.
        """
        normalized_name = self._normalize_strategy_name(strategy_name)
        strategy_class = self._strategies_by_name.get(normalized_name)
        if strategy_class is None:
            raise NotImplementedError(
                f"Devops information strategy is not implemented for '{normalized_name}'."
            )
        return strategy_class

    def execute(
            self,
            *,
            strategy_name: str,
            metadata: Dict[str, object],
    ) -> Dict[str, object]:
        """
        Execute one registered information strategy against the live registry.

        Args:
            strategy_name:
                Strategy key to resolve and execute.
            metadata:
                Caller-supplied metadata passed through to the strategy.

        Returns:
            Dict[str, object]:
                Detached strategy result payload.
        """
        normalized_name = self._normalize_strategy_name(strategy_name)
        strategy_class = self.resolve(normalized_name)
        result = strategy_class.execute(
            devops_information_registry=self._devops_information_registry,
            metadata=metadata,
        )
        self._execution_counts_by_name[normalized_name] = (
            self._execution_counts_by_name.get(normalized_name, 0) + 1
        )
        return result

    def get_execution_count(self, strategy_name: str) -> int:
        """
        Return how many times one strategy completed successfully.

        Args:
            strategy_name:
                Strategy key to look up.

        Returns:
            int: Successful execution count (0 when never run).
        """
        normalized_name = self._normalize_strategy_name(strategy_name)
        return self._execution_counts_by_name.get(normalized_name, 0)

    def list_execution_counts(self) -> Dict[str, int]:
        """
        Return a detached copy of all successful execution counts.

        Returns:
            Dict[str, int]: Normalized strategy name to successful execution
            count, for strategies that have run at least once.
        """
        return dict(self._execution_counts_by_name)

    def list_registered_strategy_names(self) -> Tuple[str, ...]:
        """
        Return the currently registered strategy names in sorted order.

        Returns:
            Tuple[str, ...]:
                Sorted registered strategy names.
        """
        return tuple(sorted(self._strategies_by_name.keys()))

    @staticmethod
    def _normalize_strategy_name(strategy_name: str) -> str:
        """
        Normalize one information-strategy name into the registry key form.

        Args:
            strategy_name:
                Candidate strategy name.

        Returns:
            str:
                Lowercased normalized strategy name.

        Raises:
            TypeError:
                If `strategy_name` is not a string.
            ValueError:
                If the normalized strategy name is empty.
        """
        if not isinstance(strategy_name, str):
            raise TypeError("strategy_name must be a string.")
        normalized_name = strategy_name.strip().lower()
        if not normalized_name:
            raise ValueError("strategy_name must not be empty.")
        return normalized_name
