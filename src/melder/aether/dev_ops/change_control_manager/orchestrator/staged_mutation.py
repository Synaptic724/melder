import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)


@dataclass(frozen=True)
class ChangeControlStagedMutation:
    """
    Immutable record describing a staged change-control mutation.

    Purpose:
        Capture staged metadata for an admitted change-control request so
        commit/abort hooks can reason about scope ownership deterministically.
    Contract:
        - Instances are immutable.
        - `request_id` and `initiator_conduit_id` must be non-empty strings.
    Args:
        request_id:
            Unique identifier of the admitted request.
        request_type:
            Change-control transaction type being staged.
        staged_at:
            Unix timestamp (seconds) when staging occurred.
        initiator_conduit_id:
            Conduit id that initiated the transaction.
        spellbook_id:
            Optional spellbook id associated with the mutation.
        conduit_ids:
            Conduit ids involved in the request.
        scope_keys:
            Normalized scope keys derived for staging/embargo checks.
        binding_keys:
            Binding keys affected by the request.
        contract_keys:
            Contract keys affected by the request.
        metadata:
            Optional metadata captured from the request.
    Returns:
        None.
    Raises:
        None.
    Threading:
        Safe to share across threads because instances are immutable.
    Lifecycle:
        Immutable; no cleanup required.
    """
    __melder_internal__ = _mrg.sentinel
    request_id: str
    request_type: ChangeTransactionType
    staged_at: float
    initiator_conduit_id: str
    spellbook_id: Optional[str]
    conduit_ids: Tuple[str, ...]
    scope_keys: Tuple[str, ...]
    binding_keys: Tuple[Tuple[str, str], ...]
    contract_keys: Tuple[Tuple[str, str, str], ...]
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_request(
            cls,
            *,
            request_id: str,
            request_type: ChangeTransactionType,
            initiator_conduit_id: str,
            spellbook_id: Optional[str],
            conduit_ids: Tuple[str, ...],
            scope_keys: Tuple[str, ...],
            binding_keys: Tuple[Tuple[str, str], ...],
            contract_keys: Tuple[Tuple[str, str, str], ...],
            metadata: Optional[Dict[str, Any]] = None,
    ) -> "ChangeControlStagedMutation":
        """
        Build a staged mutation record from request metadata.

        Purpose:
            Normalize staged metadata in a single constructor.
        Contract:
            - `scope_keys` must already be normalized.
        Args:
            request_id:
                Unique request identifier.
            request_type:
                Transaction type being staged.
            initiator_conduit_id:
                Conduit id that initiated the transaction.
            spellbook_id:
                Optional spellbook id associated with the request.
            conduit_ids:
                Conduit ids involved in the request.
            scope_keys:
                Normalized scope keys for staging.
            binding_keys:
                Binding keys affected by the request.
            contract_keys:
                Contract keys affected by the request.
            metadata:
                Optional metadata captured from the request.
        Returns:
            ChangeControlStagedMutation:
                Immutable staged mutation record.
        Raises:
            None.
        Threading:
            Thread-safe without locks; no shared state is mutated.
        """
        return cls(
            request_id=request_id,
            request_type=request_type,
            staged_at=time.time(),
            initiator_conduit_id=initiator_conduit_id,
            spellbook_id=spellbook_id,
            conduit_ids=conduit_ids,
            scope_keys=scope_keys,
            binding_keys=binding_keys,
            contract_keys=contract_keys,
            metadata=dict(metadata) if metadata else {},
        )
