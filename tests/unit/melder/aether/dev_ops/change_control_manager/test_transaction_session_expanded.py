import pytest

from melder.aether.aetheric_frame.dev_ops.change_control_manager.orchestrator.staged_mutation import (
    ChangeControlStagedMutation,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
    ChangeControlTransactionManager,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_session import (
    TransactionSession,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)
from melder.aether.aetheric_frame.dev_ops.devops_identity import DevopsIdentity


def _build_request_and_staged():
    """Build one admitted-shape request/staged pair for session tests."""
    manager = ChangeControlTransactionManager()
    request = manager.build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        spellbook_id="spellbook-1",
        scope_keys=["scope:spellbook:spellbook-1"],
    )
    staged = ChangeControlStagedMutation.from_request(
        request_id=request.request_id,
        request_type=request.request_type,
        initiator_conduit_id=request.initiator_conduit_id,
        spellbook_id=request.spellbook_id,
        conduit_ids=request.conduit_ids,
        scope_keys=request.scope_keys,
        binding_keys=request.binding_keys,
        contract_keys=request.contract_keys,
        metadata=request.metadata,
    )
    return request, staged


def test_transaction_session_init_requires_request() -> None:
    """
    Purpose:
        Verify session initialization rejects a missing request.
    Contract:
        - request must not be None.
    Returns:
        None.
    Raises:
        AssertionError: If missing requests are accepted.
    """
    _request, staged = _build_request_and_staged()

    with pytest.raises(ValueError, match="request must not be None."):
        TransactionSession(
            request=None,
            staged=staged,
            owner_thread_id=1,
        )


def test_transaction_session_init_requires_staged_payload() -> None:
    """
    Purpose:
        Verify session initialization rejects a missing staged payload.
    Contract:
        - staged must not be None.
    Returns:
        None.
    Raises:
        AssertionError: If missing staged payloads are accepted.
    """
    request, _staged = _build_request_and_staged()

    with pytest.raises(ValueError, match="staged must not be None."):
        TransactionSession(
            request=request,
            staged=None,
            owner_thread_id=1,
        )


@pytest.mark.parametrize("owner_thread_id", [0, -1, "thread"])
def test_transaction_session_init_validates_owner_thread_id(
        owner_thread_id,
) -> None:
    """
    Purpose:
        Verify session initialization validates owner-thread ids.
    Contract:
        - owner_thread_id must be a positive integer.
    Returns:
        None.
    Raises:
        AssertionError: If invalid owner-thread ids are accepted.
    """
    request, staged = _build_request_and_staged()

    with pytest.raises(ValueError, match="owner_thread_id must be a positive integer."):
        TransactionSession(
            request=request,
            staged=staged,
            owner_thread_id=owner_thread_id,
        )


def test_transaction_session_grant_capabilities_extends_supported_set() -> None:
    """
    Purpose:
        Verify capabilities can be extended after initialization.
    Contract:
        - grant_capabilities adds new entries without removing old ones.
    Returns:
        None.
    Raises:
        AssertionError: If granted capabilities are not reflected.
    """
    request, staged = _build_request_and_staged()
    session = TransactionSession(
        request=request,
        staged=staged,
        owner_thread_id=1,
        capabilities=("bind",),
    )

    session.grant_capabilities(("contract_mutation",))

    assert session.supports_capabilities(("bind", "contract_mutation")) is True


def test_transaction_session_join_rejects_closed_status() -> None:
    """
    Purpose:
        Verify join rejects closed session states.
    Contract:
        - Only open and abort_only sessions can be joined.
    Returns:
        None.
    Raises:
        AssertionError: If closed sessions can be joined.
    """
    request, staged = _build_request_and_staged()
    session = TransactionSession(
        request=request,
        staged=staged,
        owner_thread_id=1,
    )
    session.mark_committed()

    with pytest.raises(RuntimeError, match="no longer active"):
        session.join(thread_id=1)


def test_transaction_session_leave_rejects_depth_underflow() -> None:
    """
    Purpose:
        Verify leave rejects session-depth underflow.
    Contract:
        - leave raises when depth would go below zero.
    Returns:
        None.
    Raises:
        AssertionError: If underflow is silently allowed.
    """
    request, staged = _build_request_and_staged()
    session = TransactionSession(
        request=request,
        staged=staged,
        owner_thread_id=1,
    )

    assert session.leave() == 0
    with pytest.raises(RuntimeError, match="depth underflow"):
        session.leave()


def test_transaction_session_mark_abort_only_records_reason_and_error() -> None:
    """
    Purpose:
        Verify abort-only transitions record diagnostic state.
    Contract:
        - status becomes abort_only.
        - failure_reason stores the supplied reason.
    Returns:
        None.
    Raises:
        AssertionError: If abort-only state is not retained.
    """
    request, staged = _build_request_and_staged()
    session = TransactionSession(
        request=request,
        staged=staged,
        owner_thread_id=1,
    )
    error = RuntimeError("boom")

    session.mark_abort_only("failed", error)

    assert session.status == TransactionSession.STATUS_ABORT_ONLY
    assert session.failure_reason == "failed"


def test_transaction_session_status_markers_transition_as_expected() -> None:
    """
    Purpose:
        Verify explicit status-marker helpers update the session state.
    Contract:
        - mark_committing, mark_committed, and mark_aborted update status directly.
    Returns:
        None.
    Raises:
        AssertionError: If status markers drift.
    """
    request, staged = _build_request_and_staged()
    session = TransactionSession(
        request=request,
        staged=staged,
        owner_thread_id=1,
    )

    session.mark_committing()
    assert session.status == TransactionSession.STATUS_COMMITTING
    session.mark_committed()
    assert session.status == TransactionSession.STATUS_COMMITTED
    session.mark_aborted()
    assert session.status == TransactionSession.STATUS_ABORTED


def test_transaction_session_commit_pipeline_propagates_validator_failure_before_hooks() -> None:
    """
    Purpose:
        Verify commit validation failures stop later hooks.
    Contract:
        - Validators run before hooks.
        - A failing validator prevents commit hooks from running.
    Returns:
        None.
    Raises:
        AssertionError: If commit hooks run after validator failure.
    """
    request, staged = _build_request_and_staged()
    session = TransactionSession(
        request=request,
        staged=staged,
        owner_thread_id=1,
    )
    calls = []

    def _validator(_staged) -> None:
        calls.append("validator")
        raise RuntimeError("boom")

    session.register_commit_validator(_validator)
    session.register_commit_hook(lambda _staged: calls.append("hook"))

    with pytest.raises(RuntimeError, match="boom"):
        session.run_commit_pipeline()

    assert calls == ["validator"]


def test_transaction_session_abort_pipeline_collects_failures_and_continues() -> None:
    """
    Purpose:
        Verify abort pipeline records hook and rollback failures while continuing.
    Contract:
        - Abort hook failures are collected.
        - Rollback failures are also collected.
        - Later rollback actions still run in reverse order.
    Returns:
        None.
    Raises:
        AssertionError: If failure collection or ordering drifts.
    """
    request, staged = _build_request_and_staged()
    session = TransactionSession(
        request=request,
        staged=staged,
        owner_thread_id=1,
    )
    calls = []

    def _abort(_staged) -> None:
        calls.append("abort")
        raise RuntimeError("abort boom")

    def _rollback_1() -> None:
        calls.append("rollback-1")

    def _rollback_2() -> None:
        calls.append("rollback-2")
        raise RuntimeError("rollback boom")

    session.register_abort_hook(_abort)
    session.register_rollback_action(_rollback_1)
    session.register_rollback_action(_rollback_2)

    failures = session.run_abort_pipeline()

    assert calls == ["abort", "rollback-2", "rollback-1"]
    assert len(failures) == 2
    assert {type(exc) for exc in failures} == {RuntimeError}


def test_transaction_session_describe_includes_submitter_identity_and_sorted_capabilities() -> None:
    """
    Purpose:
        Verify describe returns a detached summary of session state.
    Contract:
        - submitter identity is described when present.
        - capabilities are sorted into a tuple.
    Returns:
        None.
    Raises:
        AssertionError: If the diagnostic snapshot is incomplete.
    """
    request, staged = _build_request_and_staged()
    identity = DevopsIdentity(
        owner_kind="spellbook",
        owner_id="spellbook-1",
        aetheric_frame_name="frame-1",
        available_transactions=("scan", "bind"),
    )
    session = TransactionSession(
        request=request,
        staged=staged,
        submitter_identity=identity,
        owner_thread_id=1,
        capabilities=("scan", "bind"),
    )

    described = session.describe()

    assert described["request_id"] == request.request_id
    assert described["submitter_identity"]["owner_id"] == "spellbook-1"
    assert described["capabilities"] == ("bind", "scan")


def test_transaction_session_cleanup_is_idempotent_and_blocks_reuse() -> None:
    """
    Purpose:
        Verify cleanup clears session state and blocks later access.
    Contract:
        - cleanup is idempotent.
        - Public access fails after cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup leaves the session reusable.
    """
    request, staged = _build_request_and_staged()
    session = TransactionSession(
        request=request,
        staged=staged,
        owner_thread_id=1,
    )

    session.cleanup()
    session.cleanup()

    assert not hasattr(session, "_lock")
    with pytest.raises((RuntimeError, AttributeError)):
        session.describe()
