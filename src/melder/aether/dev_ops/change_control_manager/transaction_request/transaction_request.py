from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class ChangeTransactionType(str, Enum):
    """
    Stable transaction kinds for change-control admission and tracking.

    Contract:
    - Values must remain stable because they are persisted in request payloads,
      staged mutation records, and diagnostic output.
    - The enum models mutation/change-control operations only; standalone scan
      or embargo concepts are not transaction kinds here.
    """
    __melder_internal__ = _mrg.sentinel
    BIND = "bind"
    LINK = "link"
    TRANSFER_OWNERSHIP = "transfer_ownership"
    MUTATION = "mutation"
    CLUSTER_LINK = "cluster_link"


@dataclass(frozen=True)
class ChangeControlTransactionRequest:
    """
    Immutable request payload used for admission and in-flight tracking.

    This is the canonical input record passed through conflict, embargo, and
    transaction-manager admission paths.

    Contract:
    - Instances are immutable and safe to share across threads.
    - `request_id` and `initiator_conduit_id` are expected to be non-empty.
    - Scope keys and hashes are expected to be normalized by the caller before
      construction.
    """
    __melder_internal__ = _mrg.sentinel
    request_id: str
    request_type: ChangeTransactionType
    created_at: float
    initiator_conduit_id: str
    spellbook_id: Optional[str] = None
    conduit_ids: Tuple[str, ...] = ()
    scope_keys: Tuple[str, ...] = ()
    scope_hashes: Tuple[str, ...] = ()
    binding_keys: Tuple[Tuple[str, str], ...] = ()
    contract_keys: Tuple[Tuple[str, str, str], ...] = ()
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ChangeControlAdmissionResult:
    """
    Immutable admission decision returned by change-control gating.

    Contract:
    - `admitted=True` means the request was accepted for execution.
    - `reasons`, `conflicts`, and `embargoes` provide rejection evidence when
      admission fails.
    """
    __melder_internal__ = _mrg.sentinel
    admitted: bool
    reasons: Tuple[str, ...] = ()
    conflicts: Tuple[str, ...] = ()
    embargoes: Tuple[str, ...] = ()
