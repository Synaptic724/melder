from enum import Enum
from typing import Any, Dict

from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.bind_transaction_strategy import (
    BindTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.devops_identity import (
    DevopsIdentity,
)


class TransactionStrategyBuilder:
    """
    Builder and resolver for transaction strategies.

    Purpose:
        Centralize transaction-kind policy resolution in change-control land so
        callers only submit `transaction_type + DevopsIdentity + metadata`
        and do not carry strategy logic themselves.
    """

    __slots__ = [
        "_transaction_manager",
    ]

    def __init__(self, transaction_manager: Any) -> None:
        """
        Build one strategy builder over the change-control transaction manager.
        """
        self._transaction_manager = transaction_manager

    def resolve(self, transaction_type: Any) -> Any:
        """
        Resolve the static strategy class for one transaction kind.
        """
        transaction_name = self._normalize_transaction_name(transaction_type)
        if transaction_name == "bind":
            return BindTransactionStrategy
        raise NotImplementedError(
            f"Transaction strategy is not implemented for '{transaction_name}'."
        )

    def build_start_plan(
            self,
            *,
            transaction_type: Any,
            identity: DevopsIdentity,
            metadata: Dict[str, object],
    ) -> Dict[str, object]:
        """
        Build the start plan for one transaction request.
        """
        strategy = self.resolve(transaction_type)
        return strategy.build_start_plan(
            transaction_manager=self._transaction_manager,
            identity=identity,
            metadata=metadata,
        )

    def on_start(
            self,
            *,
            transaction_type: Any,
            metadata: Dict[str, object],
    ) -> None:
        """
        Run strategy-owned start side effects for one transaction kind.
        """
        strategy = self.resolve(transaction_type)
        strategy.on_start(metadata)

    def on_end(
            self,
            *,
            transaction_type: Any,
            metadata: Dict[str, object],
    ) -> None:
        """
        Run strategy-owned end side effects for one transaction kind.
        """
        strategy = self.resolve(transaction_type)
        strategy.on_end(metadata)

    @staticmethod
    def _normalize_transaction_name(transaction_type: Any) -> str:
        """
        Normalize one transaction kind to its lowercase string value.
        """
        value = transaction_type
        if not isinstance(transaction_type, str):
            if isinstance(transaction_type, Enum):
                value = transaction_type.value
            else:
                try:
                    value = transaction_type.value
                except AttributeError as exc:
                    raise TypeError(
                        "transaction_type must be a string-like value."
                    ) from exc
        if not isinstance(value, str):
            raise TypeError("transaction_type must be a string-like value.")
        normalized_value = value.strip().lower()
        if not normalized_value:
            raise ValueError("transaction_type must not be empty.")
        return normalized_value
