import pytest

from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
    ChangeControlTransactionManager,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)
from tests._cleanup_recheck_support import CleanupRecheckHandshake


def test_transaction_manager_cleanup_is_idempotent_and_blocks_reuse() -> None:
    """
    Purpose:
        Validate cleanup clears registries and forbids later use.
    Contract:
        - cleanup() is safe to call more than once.
        - In-flight/link-mirror state and lock references are nulled after cleanup.
        - Public methods raise RuntimeError after cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup is not idempotent or reuse is allowed.
    """
    manager = ChangeControlTransactionManager()
    request = manager.build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
    )
    manager.add_in_flight(request)
    manager.register_link(
        borrower_conduit_id="borrower-1",
        provider_conduit_id="provider-1",
    )

    manager.cleanup()
    manager.cleanup()

    assert not hasattr(manager, '_in_flight')
    assert not hasattr(manager, '_link_mirror')
    assert not hasattr(manager, '_lock')

    with pytest.raises((RuntimeError, AttributeError)):
        manager.describe()


def test_transaction_manager_cleanup_rechecks_cleaned_inside_lock() -> None:
    """
    Purpose:
        Validate the inner cleanup re-check under concurrent teardown.
    Contract:
        - A second cleanup caller may pass the outer `_cleaned` check.
        - The inner `_cleaned` check inside the lock returns safely without error.
        - The handshake holds the first caller inside the lock until the second has passed the outer check and
          is about to block; the first caller then runs the real cleanup, and the second must return at the inner
          check. Without that check the teardown would run twice and a caller would raise on an attribute the
          other had already deleted.
        - Both callers must finish without raising; the manager must read cleaned with its `_lock` dropped.
        - The callers are ordered by the handshake, not by timing: the earlier hand-made lock could lose its
          signal and failed on CI (GitHub #206; TASK-2026-11-08-deterministic_cleanup_recheck_handshake).
    Returns:
        None.
    Raises:
        AssertionError: If concurrent cleanup raises or leaves the manager dirty.
    """
    manager = ChangeControlTransactionManager()
    handshake = CleanupRecheckHandshake()
    manager._lock = handshake.lock

    handshake.run(manager.cleanup)

    assert manager._cleaned is True
    assert not hasattr(manager, '_lock')


def test_transaction_manager_scope_key_helpers_validate_required_inputs() -> None:
    """
    Purpose:
        Validate helper guard clauses for required identifiers.
    Contract:
        - Empty spellbook, cluster, binding, or contract identifiers raise ValueError.
    Returns:
        None.
    Raises:
        AssertionError: If invalid identifiers are accepted.
    """
    manager = ChangeControlTransactionManager()

    with pytest.raises(ValueError, match="spellbook_id cannot be empty"):
        manager.make_scope_key_spellbook("")
    with pytest.raises(ValueError, match="cluster_id cannot be empty"):
        manager.make_scope_key_cluster("")
    with pytest.raises(ValueError, match="frame_key and binding_key are required"):
        manager.make_scope_key_binding("frame", "")
    with pytest.raises(ValueError, match="frame_key, binding_key, and peer_conduit_id are required"):
        manager.make_scope_key_contract("frame", "__default__", "")


def test_transaction_manager_link_registration_validates_required_ids() -> None:
    """
    Purpose:
        Validate borrower/provider id guards for link-mirror updates.
    Contract:
        - register_link and unregister_link reject empty borrower/provider ids.
    Returns:
        None.
    Raises:
        AssertionError: If invalid borrower/provider ids are accepted.
    """
    manager = ChangeControlTransactionManager()

    with pytest.raises(ValueError, match="borrower_conduit_id and provider_conduit_id are required"):
        manager.register_link(borrower_conduit_id="", provider_conduit_id="provider-1")
    with pytest.raises(ValueError, match="borrower_conduit_id and provider_conduit_id are required"):
        manager.unregister_link(borrower_conduit_id="borrower-1", provider_conduit_id="")


def test_transaction_manager_unregister_link_noops_for_missing_provider() -> None:
    """
    Purpose:
        Validate unregister_link safely ignores unknown providers.
    Contract:
        - Missing provider keys produce a no-op.
    Returns:
        None.
    Raises:
        AssertionError: If missing providers mutate the mirror.
    """
    manager = ChangeControlTransactionManager()

    manager.unregister_link(
        borrower_conduit_id="borrower-1",
        provider_conduit_id="missing-provider",
    )

    assert manager.describe()["link_mirror"] == {}


def test_transaction_manager_list_borrowers_for_provider_empty_id_returns_empty() -> None:
    """
    Purpose:
        Validate borrower lookup handles an empty provider id.
    Contract:
        - Empty provider ids return an empty set.
    Returns:
        None.
    Raises:
        AssertionError: If empty provider ids return borrowers.
    """
    manager = ChangeControlTransactionManager()

    assert manager.list_borrowers_for_provider("") == set()


def test_transaction_manager_describe_reports_in_flight_and_link_mirror_snapshot() -> None:
    """
    Purpose:
        Validate describe returns diagnostic snapshots for both registries.
    Contract:
        - describe includes in-flight count and link-mirror snapshot data.
    Returns:
        None.
    Raises:
        AssertionError: If the diagnostic snapshot is incomplete.
    """
    manager = ChangeControlTransactionManager()
    request = manager.build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
    )
    manager.add_in_flight(request)
    manager.register_link(
        borrower_conduit_id="borrower-1",
        provider_conduit_id="provider-1",
    )

    info = manager.describe()

    assert info["in_flight_count"] == 1
    assert info["link_mirror"] == {"provider-1": {"borrower-1"}}
