import pytest

from melder.aether.aetheric_frame.dev_ops.change_control_manager.embargo_manager.embargo_manager import (
    ChangeControlEmbargoManager,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
    ChangeControlTransactionManager,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)
from tests._cleanup_recheck_support import CleanupRecheckHandshake


def test_embargo_manager_cleanup_is_idempotent_and_blocks_reuse() -> None:
    """
    Purpose:
        Validate cleanup clears registries and forbids later use.
    Contract:
        - cleanup() is safe to call more than once.
        - Registry references and lock are nulled after cleanup.
        - Public methods raise RuntimeError after cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup is not idempotent or reuse is allowed.
    """
    manager = ChangeControlEmbargoManager()
    manager.open_embargo(
        scope_keys=["scope-a"],
        reason_tag="bind",
        owner_request_id="tx-1",
    )

    manager.cleanup()
    manager.cleanup()

    assert not hasattr(manager, '_embargoes_by_scope')
    assert not hasattr(manager, '_embargoes_by_owner')
    assert not hasattr(manager, '_lock')

    with pytest.raises((RuntimeError, AttributeError)):
        manager.find_embargoes(["scope-a"])


def test_embargo_manager_cleanup_rechecks_cleaned_inside_lock() -> None:
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
    manager = ChangeControlEmbargoManager()
    handshake = CleanupRecheckHandshake()
    manager._lock = handshake.lock

    handshake.run(manager.cleanup)

    assert manager._cleaned is True
    assert not hasattr(manager, '_lock')


def test_embargo_manager_open_and_extend_validate_required_arguments() -> None:
    """
    Purpose:
        Validate guard clauses for owner and reason arguments.
    Contract:
        - open_embargo rejects empty owner ids and reason tags.
        - extend_embargoes rejects empty owner ids and reason tags.
    Returns:
        None.
    Raises:
        AssertionError: If invalid arguments are accepted.
    """
    manager = ChangeControlEmbargoManager()

    with pytest.raises(ValueError, match="owner_request_id and reason_tag are required"):
        manager.open_embargo(scope_keys=["scope-a"], reason_tag="", owner_request_id="tx-1")
    with pytest.raises(ValueError, match="owner_request_id and reason_tag are required"):
        manager.extend_embargoes(owner_request_id="", scope_keys=["scope-a"], reason_tag="bind")


def test_embargo_manager_close_embargo_preserves_other_owner_records() -> None:
    """
    Purpose:
        Validate closing one owner leaves unrelated embargo records intact.
    Contract:
        - Shared scope keys retain records for other owners.
        - Closed owner scopes are removed from the owner index.
    Returns:
        None.
    Raises:
        AssertionError: If unrelated embargo records are removed.
    """
    manager = ChangeControlEmbargoManager()
    manager.open_embargo(scope_keys=["shared-scope"], reason_tag="bind", owner_request_id="tx-1")
    manager.open_embargo(scope_keys=["shared-scope"], reason_tag="link", owner_request_id="tx-2")

    manager.close_embargo("tx-1")

    hints = manager.list_advisory_hints(["shared-scope"])
    assert len(hints) == 1
    assert hints[0].owner_request_id == "tx-2"
    assert "tx-1" not in manager._embargoes_by_owner


def test_embargo_manager_close_embargo_ignores_empty_owner_id() -> None:
    """
    Purpose:
        Validate close_embargo treats an empty owner id as a no-op.
    Contract:
        - Empty owner ids do not mutate embargo state.
    Returns:
        None.
    Raises:
        AssertionError: If embargo state changes.
    """
    manager = ChangeControlEmbargoManager()
    manager.open_embargo(scope_keys=["scope-a"], reason_tag="bind", owner_request_id="tx-1")

    before = manager.describe()
    manager.close_embargo("")
    after = manager.describe()

    assert after == before


def test_embargo_manager_list_advisory_hints_skips_unembargoed_scopes() -> None:
    """
    Purpose:
        Validate advisory lookup skips scopes without records.
    Contract:
        - Unembargoed scopes contribute no hint records.
    Returns:
        None.
    Raises:
        AssertionError: If missing scopes create advisory hints.
    """
    manager = ChangeControlEmbargoManager()
    manager.open_embargo(scope_keys=["scope-a"], reason_tag="bind", owner_request_id="tx-1")

    hints = manager.list_advisory_hints(["scope-a", "scope-missing"])

    assert len(hints) == 1
    assert hints[0].scope_key == "scope-a"


def test_embargo_manager_collect_scope_keys_from_staged_none_returns_empty() -> None:
    """
    Purpose:
        Validate staged scope collection handles a missing staged mutation.
    Contract:
        - None staged input returns an empty tuple.
    Returns:
        None.
    Raises:
        AssertionError: If None staged input produces scope keys.
    """
    manager = ChangeControlEmbargoManager()

    assert manager.collect_scope_keys_from_staged(None) == ()


def test_embargo_manager_apply_implicit_embargoes_noops_without_scopes() -> None:
    """
    Purpose:
        Validate implicit embargo application no-ops for scope-free requests.
    Contract:
        - Requests with no explicit or derived scope keys do not open embargoes.
    Returns:
        None.
    Raises:
        AssertionError: If empty-scope requests create embargoes.
    """
    manager = ChangeControlEmbargoManager()
    request = ChangeControlTransactionManager().build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
    )

    manager.apply_implicit_embargoes(request)

    assert manager.describe()["embargo_count"] == 0


def test_embargo_manager_describe_reports_scope_snapshot() -> None:
    """
    Purpose:
        Validate describe returns embargoed scope and count snapshots.
    Contract:
        - describe reports current scope keys and aggregate embargo count.
    Returns:
        None.
    Raises:
        AssertionError: If the snapshot is incomplete.
    """
    manager = ChangeControlEmbargoManager()
    manager.open_embargo(scope_keys=["scope-a", "scope-b"], reason_tag="bind", owner_request_id="tx-1")

    info = manager.describe()

    assert set(info["embargoed_scopes"]) == {"scope-a", "scope-b"}
    assert info["embargo_count"] == 2
