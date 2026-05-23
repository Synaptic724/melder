from dataclasses import FrozenInstanceError

import pytest

from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeControlAdmissionResult,
    ChangeControlTransactionRequest,
    ChangeTransactionType,
)


def test_change_transaction_type_values_remain_stable() -> None:
    """
    Purpose:
        Verify transaction-type string values stay stable.
    Contract:
        - Enum values are the canonical payload values used by runtime callers.
    Returns:
        None.
    Raises:
        AssertionError: If transaction type values drift.
    """
    assert ChangeTransactionType.BIND.value == "bind"
    assert ChangeTransactionType.LINK.value == "link"
    assert ChangeTransactionType.TRANSFER_OWNERSHIP.value == "transfer_ownership"
    assert ChangeTransactionType.MUTATION.value == "mutation"
    assert ChangeTransactionType.CLUSTER_LINK.value == "cluster_link"


def test_change_control_transaction_request_defaults_are_empty_and_immutable() -> None:
    """
    Purpose:
        Verify request payload defaults are stable and immutable.
    Contract:
        - Optional tuple fields default to empty tuples.
        - metadata defaults to an empty dict.
        - The dataclass is frozen.
    Returns:
        None.
    Raises:
        AssertionError: If defaults drift or mutability is allowed.
    """
    request = ChangeControlTransactionRequest(
        request_id="tx-1",
        request_type=ChangeTransactionType.BIND,
        created_at=1.0,
        initiator_conduit_id="conduit-1",
    )

    assert request.spellbook_id is None
    assert request.conduit_ids == ()
    assert request.scope_keys == ()
    assert request.scope_hashes == ()
    assert request.binding_keys == ()
    assert request.contract_keys == ()
    assert request.metadata == {}

    with pytest.raises(FrozenInstanceError):
        request.request_id = "tx-2"


def test_change_control_transaction_request_preserves_explicit_payloads() -> None:
    """
    Purpose:
        Verify explicit payload values are retained exactly.
    Contract:
        - Supplied tuples and metadata are stored on the frozen payload.
    Returns:
        None.
    Raises:
        AssertionError: If explicit payload fields drift.
    """
    request = ChangeControlTransactionRequest(
        request_id="tx-1",
        request_type=ChangeTransactionType.LINK,
        created_at=2.0,
        initiator_conduit_id="conduit-1",
        spellbook_id="spellbook-1",
        conduit_ids=("conduit-1", "conduit-2"),
        scope_keys=("scope:spellbook:spellbook-1",),
        scope_hashes=("hash-1",),
        binding_keys=(("frame", "__default__"),),
        contract_keys=(("frame", "__default__", "conduit-2"),),
        metadata={"origin_surface": "spellbook.bind"},
    )

    assert request.request_type is ChangeTransactionType.LINK
    assert request.spellbook_id == "spellbook-1"
    assert request.conduit_ids == ("conduit-1", "conduit-2")
    assert request.scope_keys == ("scope:spellbook:spellbook-1",)
    assert request.scope_hashes == ("hash-1",)
    assert request.binding_keys == (("frame", "__default__"),)
    assert request.contract_keys == (("frame", "__default__", "conduit-2"),)
    assert request.metadata == {"origin_surface": "spellbook.bind"}


def test_change_control_admission_result_defaults_are_empty_and_immutable() -> None:
    """
    Purpose:
        Verify admission-result defaults are stable and immutable.
    Contract:
        - reasons, conflicts, and embargoes default to empty tuples.
        - The dataclass is frozen.
    Returns:
        None.
    Raises:
        AssertionError: If defaults drift or mutability is allowed.
    """
    result = ChangeControlAdmissionResult(admitted=True)

    assert result.reasons == ()
    assert result.conflicts == ()
    assert result.embargoes == ()

    with pytest.raises(FrozenInstanceError):
        result.admitted = False


def test_change_control_admission_result_preserves_rejection_payloads() -> None:
    """
    Purpose:
        Verify explicit rejection evidence is retained.
    Contract:
        - reasons, conflicts, and embargoes are stored exactly as supplied.
    Returns:
        None.
    Raises:
        AssertionError: If rejection payloads drift.
    """
    result = ChangeControlAdmissionResult(
        admitted=False,
        reasons=("conflict", "embargo"),
        conflicts=("tx-1",),
        embargoes=("scope:spellbook:spellbook-1",),
    )

    assert result.admitted is False
    assert result.reasons == ("conflict", "embargo")
    assert result.conflicts == ("tx-1",)
    assert result.embargoes == ("scope:spellbook:spellbook-1",)
