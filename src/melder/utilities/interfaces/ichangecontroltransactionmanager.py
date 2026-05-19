from typing import Any, Dict, Iterable, Optional, Protocol, Tuple, runtime_checkable
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeControlTransactionRequest,
    ChangeTransactionType,
)


@runtime_checkable
class IChangeControlTransactionManager(Protocol):
    """
    Interface for the change-control transaction request manager.

    Purpose:
        Define the request-construction and link-mirror surface consumed by
        higher-level spellbook and runtime transaction code.
    """

    def build_request(
            self,
            *,
            request_type: ChangeTransactionType,
            initiator_conduit_id: str,
            spellbook_id: Optional[str] = None,
            conduit_ids: Optional[Iterable[str]] = None,
            scope_keys: Optional[Iterable[str]] = None,
            scope_hashes: Optional[Iterable[str]] = None,
            binding_keys: Optional[Iterable[Tuple[str, str]]] = None,
            contract_keys: Optional[Iterable[Tuple[str, str, str]]] = None,
            metadata: Optional[Dict[str, Any]] = None,
    ) -> ChangeControlTransactionRequest:
        """
        Build one immutable transaction request payload.
        """
        ...

    def make_scope_key_spellbook(self, spellbook_id: str) -> str:
        """
        Return the canonical scope key for one spellbook id.
        """
        ...

    def register_link(
            self,
            *,
            borrower_conduit_id: str,
            provider_conduit_id: str,
    ) -> None:
        """
        Track one borrower/provider conduit link.
        """
        ...

    def unregister_link(
            self,
            *,
            borrower_conduit_id: str,
            provider_conduit_id: str,
    ) -> None:
        """
        Remove one borrower/provider conduit link.
        """
        ...
