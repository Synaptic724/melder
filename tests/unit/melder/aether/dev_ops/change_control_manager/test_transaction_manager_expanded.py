from typing import Any, Dict

import pytest

from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
    ChangeControlTransactionManager,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)


def test_transaction_manager_build_request_validates_initiator_type() -> None:
    """
    Purpose:
        Verify request construction rejects non-string initiator ids.
    Contract:
        - initiator_conduit_id must be a string.
    Returns:
        None.
    Raises:
        AssertionError: If non-string initiator ids are accepted.
    """
    manager = ChangeControlTransactionManager()

    with pytest.raises(TypeError, match="initiator_conduit_id must be a string."):
        manager.build_request(
            request_type=ChangeTransactionType.BIND,
            initiator_conduit_id=1,
        )


def test_transaction_manager_build_request_validates_initiator_presence() -> None:
    """
    Purpose:
        Verify request construction rejects empty initiator ids.
    Contract:
        - initiator_conduit_id must not be empty.
    Returns:
        None.
    Raises:
        AssertionError: If empty initiator ids are accepted.
    """
    manager = ChangeControlTransactionManager()

    with pytest.raises(ValueError, match="initiator_conduit_id must not be empty."):
        manager.build_request(
            request_type=ChangeTransactionType.BIND,
            initiator_conduit_id=" ",
        )


def test_transaction_manager_build_request_derives_deterministic_scope_hashes() -> None:
    """
    Purpose:
        Verify scope hashes are derived from normalized scope keys.
    Contract:
        - Duplicate scope keys do not produce duplicate hashes.
        - Hash ordering is deterministic.
    Returns:
        None.
    Raises:
        AssertionError: If derived hashes are unstable.
    """
    manager = ChangeControlTransactionManager()

    request = manager.build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        scope_keys=("scope:b", "scope:a", "scope:b"),
    )

    assert len(request.scope_hashes) == 2
    assert request.scope_hashes == manager._normalize_scope_hashes(
        ("scope:b", "scope:a", "scope:b")
    )


def test_transaction_manager_build_request_preserves_explicit_hashes_without_deriving() -> None:
    """
    Purpose:
        Verify explicit scope hashes are preserved as supplied.
    Contract:
        - Provided scope_hashes win over derivation from scope_keys.
    Returns:
        None.
    Raises:
        AssertionError: If explicit hashes are replaced.
    """
    manager = ChangeControlTransactionManager()

    request = manager.build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        scope_keys=("scope:a",),
        scope_hashes=("hash-a",),
    )

    assert request.scope_hashes == ("hash-a",)


def test_transaction_manager_build_request_copies_metadata() -> None:
    """
    Purpose:
        Verify request metadata is copied on construction.
    Contract:
        - Caller mutation after construction does not affect the request payload.
    Returns:
        None.
    Raises:
        AssertionError: If metadata is retained by reference.
    """
    manager = ChangeControlTransactionManager()
    metadata: Dict[str, Any] = {"origin": "bind"}

    request = manager.build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        metadata=metadata,
    )
    metadata["origin"] = "mutated"

    assert request.metadata == {"origin": "bind"}


def test_transaction_manager_scope_key_identity_builds_normalized_scope() -> None:
    """
    Purpose:
        Verify identity scope keys normalize owner kind and id.
    Contract:
        - Scope key format is `scope:<owner_kind>:<owner_id>`.
    Returns:
        None.
    Raises:
        AssertionError: If scope key normalization drifts.
    """
    manager = ChangeControlTransactionManager()

    assert (
        manager.make_scope_key_identity(
            owner_kind="conduit_ward",
            owner_id="conduit-1",
        )
        == "scope:conduit_ward:conduit-1"
    )


def test_transaction_manager_scope_key_identity_validates_inputs() -> None:
    """
    Purpose:
        Verify identity scope helper rejects empty fields.
    Contract:
        - owner_kind and owner_id are required.
    Returns:
        None.
    Raises:
        AssertionError: If empty identity fields are accepted.
    """
    manager = ChangeControlTransactionManager()

    with pytest.raises(ValueError, match="owner_kind cannot be empty"):
        manager.make_scope_key_identity(owner_kind="", owner_id="conduit-1")
    with pytest.raises(ValueError, match="owner_id cannot be empty"):
        manager.make_scope_key_identity(owner_kind="conduit", owner_id="")


def test_transaction_manager_scope_key_transaction_owner_builds_normalized_scope() -> None:
    """
    Purpose:
        Verify transaction-owner scope keys normalize all parts.
    Contract:
        - Scope key format is `scope:transaction:<owner_kind>:<owner_id>:<transaction_name>`.
    Returns:
        None.
    Raises:
        AssertionError: If scope key normalization drifts.
    """
    manager = ChangeControlTransactionManager()

    assert (
        manager.make_scope_key_transaction_owner(
            owner_kind="spellbook",
            owner_id="spellbook-1",
            transaction_name="bind",
        )
        == "scope:transaction:spellbook:spellbook-1:bind"
    )


def test_transaction_manager_scope_key_transaction_owner_validates_inputs() -> None:
    """
    Purpose:
        Verify transaction-owner scope helper rejects empty fields.
    Contract:
        - owner_kind, owner_id, and transaction_name are required.
    Returns:
        None.
    Raises:
        AssertionError: If empty transaction-owner fields are accepted.
    """
    manager = ChangeControlTransactionManager()

    with pytest.raises(ValueError, match="owner_kind cannot be empty"):
        manager.make_scope_key_transaction_owner(
            owner_kind="",
            owner_id="spellbook-1",
            transaction_name="bind",
        )
    with pytest.raises(ValueError, match="owner_id cannot be empty"):
        manager.make_scope_key_transaction_owner(
            owner_kind="spellbook",
            owner_id="",
            transaction_name="bind",
        )
    with pytest.raises(ValueError, match="transaction_name cannot be empty"):
        manager.make_scope_key_transaction_owner(
            owner_kind="spellbook",
            owner_id="spellbook-1",
            transaction_name="",
        )


def test_transaction_manager_add_in_flight_replaces_same_request_id() -> None:
    """
    Purpose:
        Verify in-flight registration is last-write-wins per request id.
    Contract:
        - Later requests with the same request id replace earlier entries.
    Returns:
        None.
    Raises:
        AssertionError: If same-id replacement fails.
    """
    manager = ChangeControlTransactionManager()
    request_a = manager.build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
    )
    request_b = manager.build_request(
        request_type=ChangeTransactionType.LINK,
        initiator_conduit_id="conduit-2",
    )
    request_b = type(request_b)(
        request_id=request_a.request_id,
        request_type=request_b.request_type,
        created_at=request_b.created_at,
        initiator_conduit_id=request_b.initiator_conduit_id,
        spellbook_id=request_b.spellbook_id,
        conduit_ids=request_b.conduit_ids,
        scope_keys=request_b.scope_keys,
        scope_hashes=request_b.scope_hashes,
        binding_keys=request_b.binding_keys,
        contract_keys=request_b.contract_keys,
        metadata=request_b.metadata,
    )

    manager.add_in_flight(request_a)
    manager.add_in_flight(request_b)

    assert manager.get_in_flight(request_a.request_id) is request_b
    assert manager.list_in_flight() == [request_b]


def test_transaction_manager_set_audit_logger_invokes_callback_on_add_in_flight() -> None:
    """
    Purpose:
        Verify the audit callback is invoked after in-flight registration.
    Contract:
        - add_in_flight invokes the configured callback with the admitted request.
    Returns:
        None.
    Raises:
        AssertionError: If audit callback is not invoked.
    """
    manager = ChangeControlTransactionManager()
    request = manager.build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
    )
    seen = []
    manager.set_audit_logger(lambda admitted: seen.append(admitted))

    manager.add_in_flight(request)

    assert seen == [request]


def test_transaction_manager_remove_in_flight_missing_id_noops() -> None:
    """
    Purpose:
        Verify missing in-flight ids are ignored.
    Contract:
        - remove_in_flight does not raise on unknown ids.
    Returns:
        None.
    Raises:
        AssertionError: If missing ids mutate state unexpectedly.
    """
    manager = ChangeControlTransactionManager()

    manager.remove_in_flight("missing")

    assert manager.list_in_flight() == []


def test_transaction_manager_get_in_flight_missing_id_returns_none() -> None:
    """
    Purpose:
        Verify missing in-flight ids return None.
    Contract:
        - get_in_flight returns None when the id is not tracked.
    Returns:
        None.
    Raises:
        AssertionError: If missing ids return junk.
    """
    manager = ChangeControlTransactionManager()

    assert manager.get_in_flight("missing") is None


def test_transaction_manager_register_link_deduplicates_borrowers() -> None:
    """
    Purpose:
        Verify repeated link registration does not duplicate borrower ids.
    Contract:
        - Borrower ids are stored in a set.
    Returns:
        None.
    Raises:
        AssertionError: If duplicate borrower entries appear.
    """
    manager = ChangeControlTransactionManager()

    manager.register_link(
        borrower_conduit_id="borrower-1",
        provider_conduit_id="provider-1",
    )
    manager.register_link(
        borrower_conduit_id="borrower-1",
        provider_conduit_id="provider-1",
    )

    assert manager.list_borrowers_for_provider("provider-1") == {"borrower-1"}


def test_transaction_manager_list_borrowers_for_provider_returns_detached_snapshot() -> None:
    """
    Purpose:
        Verify borrower snapshots are detached from internal state.
    Contract:
        - Returned borrower sets can be mutated without affecting the manager.
    Returns:
        None.
    Raises:
        AssertionError: If snapshot mutation leaks back.
    """
    manager = ChangeControlTransactionManager()
    manager.register_link(
        borrower_conduit_id="borrower-1",
        provider_conduit_id="provider-1",
    )

    borrowers = manager.list_borrowers_for_provider("provider-1")
    borrowers.add("borrower-2")

    assert manager.list_borrowers_for_provider("provider-1") == {"borrower-1"}
