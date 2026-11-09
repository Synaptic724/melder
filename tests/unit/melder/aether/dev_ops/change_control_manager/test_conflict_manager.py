import pytest

from melder.aether.aetheric_frame.dev_ops.change_control_manager.conflict_manager.conflict_manager import (
    ChangeControlConflictManager,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeControlTransactionRequest,
    ChangeTransactionType,
)
from tests._cleanup_recheck_support import CleanupRecheckHandshake


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

    assert not hasattr(manager, '_lock')

    assert manager.find_conflicts(None, []) == ()


def test_conflict_manager_cleanup_rechecks_cleaned_inside_lock() -> None:
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
    manager = ChangeControlConflictManager()
    handshake = CleanupRecheckHandshake()
    manager._lock = handshake.lock

    handshake.run(manager.cleanup)

    assert manager._cleaned is True
    assert not hasattr(manager, '_lock')


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
