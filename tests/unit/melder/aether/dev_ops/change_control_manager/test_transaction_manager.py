from threading import Event, RLock, Thread

import pytest

from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
    ChangeControlTransactionManager,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)


class _CoordinatedLock:
    def __init__(self) -> None:
        self._entered_first: Event = Event()
        self._second_attempted: Event = Event()
        self._lock: RLock = RLock()

    def __enter__(self):
        if self._entered_first.is_set():
            self._second_attempted.set()
        self._lock.acquire()
        if not self._entered_first.is_set():
            self._entered_first.set()
            assert self._second_attempted.wait(timeout=1.0)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self._lock.release()


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

    with pytest.raises(RuntimeError):
        manager.describe()


def test_transaction_manager_cleanup_rechecks_cleaned_inside_lock() -> None:
    """
    Purpose:
        Validate the inner cleanup re-check under concurrent teardown.
    Contract:
        - A second cleanup caller may pass the outer `_cleaned` check.
        - The inner `_cleaned` check inside the lock returns safely without error.
    Returns:
        None.
    Raises:
        AssertionError: If concurrent cleanup raises or leaves the manager dirty.
    """
    manager = ChangeControlTransactionManager()
    manager._lock = _CoordinatedLock()
    failures: list[BaseException] = []

    def _run_cleanup() -> None:
        try:
            manager.cleanup()
        except BaseException as exc:
            failures.append(exc)

    first = Thread(target=_run_cleanup, name="tx-cleanup-first")
    second = Thread(target=_run_cleanup, name="tx-cleanup-second")

    first.start()
    assert manager._lock._entered_first.wait(timeout=1.0)
    second.start()
    first.join()
    second.join()

    assert failures == []
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
