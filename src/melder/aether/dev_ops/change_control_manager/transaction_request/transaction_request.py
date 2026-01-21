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
    Args:
        None.
    Returns:
        None.
    Raises:
        None.
    Threading:
        Stateless; safe to share across threads.
    Lifecycle:
        No cleanup required.
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
    Immutable transaction request payload for admission and tracking.

    Purpose:
        Provide a stable, immutable record of a mutation request so admission,
        conflict, and embargo checks can be performed deterministically.
    Contract:
        - Instances are immutable.
        - `request_id` and `initiator_conduit_id` must be non-empty strings.
        - Scope keys and hashes must be normalized by the caller.
    Args:
        request_id:
            Unique identifier for the request.
        request_type:
            Change-control transaction type.
        created_at:
            Unix timestamp (seconds) when the request was created.
        initiator_conduit_id:
            Conduit id initiating the request.
        spellbook_id:
            Optional spellbook id associated with the request.
        conduit_ids:
            Conduit ids participating in the request.
        scope_keys:
            Normalized scope keys derived by the caller.
        scope_hashes:
            Normalized scope hashes derived by the caller.
        binding_keys:
            Binding keys affected by the request.
        contract_keys:
            Contract keys affected by the request.
        metadata:
            Caller-supplied metadata for diagnostics.
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
    Args:
        admitted:
            True if the request was accepted for execution.
        reasons:
            Short reason codes explaining a rejection, if any.
        conflicts:
            Conflicting request ids, if any.
        embargoes:
            Embargoed scope keys, if any.
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
    admitted: bool
    reasons: Tuple[str, ...] = ()
    conflicts: Tuple[str, ...] = ()
    embargoes: Tuple[str, ...] = ()
