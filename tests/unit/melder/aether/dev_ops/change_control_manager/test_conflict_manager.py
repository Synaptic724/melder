import pytest
from threading import Event, RLock, Thread

from melder.aether.dev_ops.change_control_manager.conflict_manager.conflict_manager import (
    ChangeControlConflictManager,
)
from melder.aether.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
    ChangeControlTransactionManager,
)
from melder.aether.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeControlTransactionRequest,
    ChangeTransactionType,
)


def test_conflict_manager_cleanup_is_idempotent_and_blocks_reuse() -> None:
    """
    Purpose:
        Validate cleanup nulls the lock and forbids later use.
    Contract:
        - cleanup() is safe to call more than once.
        - After cleanup, public conflict checks raise RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup is not idempotent or reuse is allowed.
    """
    manager = ChangeControlConflictManager()
    manager.cleanup()
    manager.cleanup()

    assert manager._lock is None

    with pytest.raises(RuntimeError):
        manager.find_conflicts(None, [])


def test_conflict_manager_cleanup_rechecks_cleaned_inside_lock() -> None:
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

    manager = ChangeControlConflictManager()
    coordinated_lock = _CoordinatedLock()
    manager._lock = coordinated_lock
    failures: list[BaseException] = []

    def _run_cleanup() -> None:
        try:
            manager.cleanup()
        except BaseException as exc:
            failures.append(exc)

    first = Thread(target=_run_cleanup, name="cleanup-first")
    second = Thread(target=_run_cleanup, name="cleanup-second")

    first.start()
    assert coordinated_lock._entered_first.wait(timeout=1.0)
    second.start()
    first.join()
    second.join()

    assert failures == []
    assert manager._cleaned is True
    assert manager._lock is None


def test_conflict_manager_find_conflicts_returns_empty_for_none_request() -> None:
    """
    Purpose:
        Validate `find_conflicts` treats a missing incoming request as a no-op.
    Contract:
        - A None request returns an empty tuple.
        - In-flight requests are not inspected when no incoming request exists.
    Returns:
        None.
    Raises:
        AssertionError: If a None request reports conflicts.
    """
    manager = ChangeControlConflictManager()

    assert manager.find_conflicts(None, []) == ()


def test_conflict_manager_detects_key_only_overlap_without_hashes() -> None:
    """
    Purpose:
        Validate raw scope-key overlap works when neither request carries hashes.
    Contract:
        - Matching scope keys yield the active request id as a conflict.
        - The raw-key branch is used even when scope_hashes are empty.
    Returns:
        None.
    Raises:
        AssertionError: If key-only overlap is missed.
    """
    conflict_manager = ChangeControlConflictManager()

    active = ChangeControlTransactionRequest(
        request_id="tx-active-key-only",
        request_type=ChangeTransactionType.BIND,
        created_at=0.0,
        initiator_conduit_id="conduit-active",
        scope_keys=("shared-scope",),
        scope_hashes=(),
    )
    incoming = ChangeControlTransactionRequest(
        request_id="tx-incoming-key-only",
        request_type=ChangeTransactionType.LINK,
        created_at=0.0,
        initiator_conduit_id="conduit-incoming",
        scope_keys=("shared-scope",),
        scope_hashes=(),
    )

    assert conflict_manager.find_conflicts(incoming, [active]) == (active.request_id,)
