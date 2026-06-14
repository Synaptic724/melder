from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Dict, Optional, Tuple, ClassVar


# Melder imports
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class ChangeTransactionType(StrEnum):
    """
    Change-control transaction types.

    Purpose:
        Enumerate the supported mutation transaction kinds used by the
        change-control admission system.
    Contract:
        - Values must remain stable because they become part of transaction
          request payloads and logs.
        - Uses `StrEnum` so runtime callers can pass members through normal
          string-oriented APIs without special casing.
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
    UNLINK = "unlink"
    NOTCH = "notch"
    ADD_TO_INDEX = "add_to_index"
    REMOVE_FROM_INDEX = "remove_from_index"


@dataclass(frozen=True)
class ChangeControlTransactionRequest:
    """
    Immutable transaction request payload for admission and tracking.

    Purpose:
        Provide a stable, immutable record of a mutation request so admission,
        conflict, embargo, and staging checks can be performed deterministically
        before any request becomes in-flight.
    Contract:
        - Instances are immutable.
        - `request_id` and `initiator_conduit_id` must be non-empty strings.
        - Scope keys and hashes must already be normalized by the caller or by
          the transaction-manager construction helpers.
        - The payload is the canonical pre-admission record later consumed by
          the orchestrator and transaction manager.
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
        scope_claims:
            Optional `(scope_key, mode)` pairs declaring per-scope claim modes
            for acquisition. Keys without an explicit pair default to
            exclusive mode at admission.
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
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    request_id: str
    request_type: ChangeTransactionType
    created_at: float
    initiator_conduit_id: str
    spellbook_id: Optional[str] = None
    conduit_ids: Tuple[str, ...] = ()
    scope_keys: Tuple[str, ...] = ()
    scope_claims: Tuple[Tuple[str, str], ...] = ()
    scope_hashes: Tuple[str, ...] = ()
    binding_keys: Tuple[Tuple[str, str], ...] = ()
    contract_keys: Tuple[Tuple[str, str, str], ...] = ()
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ChangeControlAdmissionResult:
    """
    Admission decision for a change-control transaction request.

    Purpose:
        Capture the orchestrator's admission outcome together with the concrete
        conflict and embargo evidence that explains a rejection.
    Contract:
        - `admitted=True` implies the request was accepted for execution.
        - `conflicts` and `embargoes` contain identifiers explaining rejection.
        - `reasons` is a compact machine-readable explanation layer that callers
          can inspect without parsing the identifier tuples.
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
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    admitted: bool
    reasons: Tuple[str, ...] = ()
    conflicts: Tuple[str, ...] = ()
    embargoes: Tuple[str, ...] = ()
