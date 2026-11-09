from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Dict, Optional, Tuple, ClassVar


# Melder imports


class ChangeTransactionType(StrEnum):
    """
    Change-control transaction types.

    Purpose:
        Enumerate the supported mutation transaction kinds used by the
        change-control admission system.

    Contract:
        - Values match member names exactly. Historical lowercase inputs and
          reporting tokens remain available for requests and logs.
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

    Registration:
        MELDER KERNEL - guarded. A value enum in request payloads and logs;
        never bound.

    Subsystem Context:
        The vocabulary of the `change_control_manager` subsystem: every
        `ChangeControlTransactionRequest` carries one member, the strategy
        builder maps each to its `TransactionStrategy`, and the mediator/embargo
        path normalizes and matches on these names. The set is exactly the
        structural mutations the DGR admits - bind/conjure, the link and cluster
        family, transfer/notch, and the index/contract verbs.

    System Context:
        This enum is the closed list of "things that can change the graph under
        change control." That it is closed and stable is the point: admission,
        conflict detection, embargo claims, and the per-type strategies all key
        on these names, so adding a structural operation means adding a member
        here plus a strategy - not threading a new ad-hoc string through the
        whole control plane. Scan and embargo are deliberately NOT modeled as
        transaction types (they are not user-driven graph mutations).

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Change-control transaction types. Melder kernel machinery: read it to
        understand the runtime, do not drive it directly.
    """
    BIND = "BIND"
    CONJURE = "CONJURE"
    LINK = "LINK"
    TRANSFER_OWNERSHIP = "TRANSFER_OWNERSHIP"
    MUTATION = "MUTATION"
    CLUSTER_LINK = "CLUSTER_LINK"
    UNLINK = "UNLINK"
    ADD_SPELL_OR_INDEX_TO_CONTRACT = "ADD_SPELL_OR_INDEX_TO_CONTRACT"
    REMOVE_SPELL_OR_INDEX_FROM_CONTRACT = "REMOVE_SPELL_OR_INDEX_FROM_CONTRACT"
    NOTCH = "NOTCH"
    ADD_TO_INDEX = "ADD_TO_INDEX"
    REMOVE_FROM_INDEX = "REMOVE_FROM_INDEX"
    ELECT_CONDUIT_CLUSTER_LEADER = "ELECT_CONDUIT_CLUSTER_LEADER"
    UNELECT_CONDUIT_CLUSTER_LEADER = "UNELECT_CONDUIT_CLUSTER_LEADER"
    CLUSTER_JOIN = "CLUSTER_JOIN"
    CLUSTER_LEAVE = "CLUSTER_LEAVE"

    @classmethod
    def _missing_(cls, value: object) -> Optional[ChangeTransactionType]:
        """
        Resolve the exact historical lowercase transaction values.

        Args:
            value: An input not already matched by the enum constructor.

        Returns:
            Optional[ChangeTransactionType]: The original member, or None for
                an unrecognized token.
        """
        if isinstance(value, str):
            for member in cls:
                if value == member.name.lower():
                    return member
        return None

    @property
    def wire_value(self) -> str:
        """
        Return the original lowercase token used in operational records.

        Returns:
            str: The historical value of this transaction type.
        """
        return self.name.lower()

    @classmethod
    def _comparison_token(cls, value: object) -> object:
        """
        Project recognized transaction forms to their historical comparison token.

        Contract:
            This enum's members and exact canonical plain strings use their
            historical lowercase value. Other objects, including unrecognized
            strings and foreign enum members, are returned unchanged. The enum's
            own value, equality, hash and serialized representation do not change.

        Args:
            value: Transaction value to compare without changing the request.

        Returns:
            object: The historical token for a recognized form, else the input.
        """
        if isinstance(value, cls):
            return value.wire_value
        if type(value) is str:
            member = cls.__members__.get(value)
            if member is not None:
                return member.wire_value
        return value


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

    Registration:
        MELDER KERNEL - guarded. Built by the transaction-manager construction
        helpers from a strategy's start plan; never user-constructed.

    Subsystem Context:
        The canonical PRE-admission record of the `change_control_manager`
        subsystem - the inverse of `ChangeControlStagedMutation` (its
        post-admission counterpart). A transaction strategy's `build_start_plan`
        produces the normalized scope keys, claims, and metadata that populate
        one of these; admission (conflict + embargo) then adjudicates it, and on
        acceptance the orchestrator stages it.

    System Context:
        Freezing the request BEFORE admission is what makes admission
        deterministic and replayable: conflict detection and scope-claim
        acquisition read a fixed snapshot, so the same request cannot admit
        differently depending on when its fields are read. The `scope_claims`
        field is where a strategy expresses its concurrency intent per key
        (exclusive/shared/intent); everything downstream - who blocks whom, what
        the lock table records - follows from these normalized keys and modes.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Immutable transaction request payload for admission and tracking.
        Melder kernel machinery: read it to understand the runtime, do not drive it directly.
    """
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

    Registration:
        MELDER KERNEL - guarded. Returned by the orchestrator's admission path;
        never user-constructed.

    Subsystem Context:
        The verdict object of the `change_control_manager` admission gate. The
        orchestrator produces one per `ChangeControlTransactionRequest`:
        `admitted=True` proceeds to staging, while a rejection carries the
        concrete `conflicts` (blocking request ids) and `embargoes` (contended
        scope keys) plus compact `reasons` codes.

    System Context:
        Returning EVIDENCE rather than a bare bool is what makes admission
        debuggable and retry-able: a blocked transaction sees exactly which
        request or scope key stopped it and waits scope-locally for that specific
        release, and an operator inspecting a stuck mutation reads why it was
        refused without decoding lock-table internals. The `reasons` layer keeps
        that explanation machine-readable so callers branch on it without parsing
        identifier tuples.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Admission decision for a change-control transaction request. Melder
        kernel machinery: read it to understand the runtime, do not drive it directly.
    """
    admitted: bool
    reasons: Tuple[str, ...] = ()
    conflicts: Tuple[str, ...] = ()
    embargoes: Tuple[str, ...] = ()
