from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class ChangeTransactionType(str, Enum):
    """
    Change-control transaction types.

    Purpose:
        Enumerate the supported mutation transaction kinds used by the
        change-control admission system.
    Contract:
        - Values must remain stable because they become part of transaction
          request payloads and logs.
        - No "scan" or "embargo" transaction types are modeled here.
    """
    __melder_internal__ = _mrg.sentinel
    BIND = "bind"
    LINK = "link"
    UNLINK = "unlink"
    TRANSFER_OWNERSHIP = "transfer_ownership"
    MUTATION = "mutation"
    CLUSTER_SHARE = "cluster_share"


@dataclass(frozen=True)
class ChangeControlTransactionRequest:
    """
    Immutable transaction request payload for admission and tracking.

    Purpose:
        Provide a stable, immutable record of a mutation request so admission,
        conflict, and embargo checks can be performed deterministically.
    Contract:
        - Instances are immutable.
        - `request_id` and `initiator_conduit_id` must be non-empty strings.
        - Scope keys and hashes must be normalized by the caller.
    Threading:
        Safe to share across threads because instances are immutable.
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
    Admission decision for a change-control transaction request.

    Purpose:
        Capture admission outcomes and conflict/embargo evidence for callers.
    Contract:
        - `admitted=True` implies the request was accepted for execution.
        - `conflicts` and `embargoes` contain identifiers explaining rejection.
    Threading:
        Safe to share across threads because instances are immutable.
    """
    __melder_internal__ = _mrg.sentinel
    admitted: bool
    reasons: Tuple[str, ...] = ()
    conflicts: Tuple[str, ...] = ()
    embargoes: Tuple[str, ...] = ()
