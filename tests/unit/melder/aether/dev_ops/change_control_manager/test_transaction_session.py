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


def test_transaction_session_initializes_open_at_depth_one() -> None:
    """A fresh session should start open, owned, and at root depth."""
    request, staged = _build_request_and_staged()
    session = TransactionSession(
        request=request,
        staged=staged,
        owner_thread_id=1,
        capabilities=("bind",),
    )

    assert session.request is request
    assert session.staged is staged
    assert session.owner_thread_id == 1
    assert session.depth == 1
    assert session.status == TransactionSession.STATUS_OPEN
    assert session.supports_capabilities(("bind",)) is True


def test_transaction_session_join_increments_depth_for_same_thread() -> None:
    """Same-thread join should reuse the session and increment depth."""
    request, staged = _build_request_and_staged()
    session = TransactionSession(
        request=request,
        staged=staged,
        owner_thread_id=11,
        capabilities=("contract_mutation",),
    )

    session.join(
        thread_id=11,
        required_capabilities=("contract_mutation",),
    )

    assert session.depth == 2
    assert session.leave() == 1


def test_transaction_session_join_rejects_other_thread() -> None:
    """Cross-thread join should be rejected explicitly."""
    request, staged = _build_request_and_staged()
    session = TransactionSession(
        request=request,
        staged=staged,
        owner_thread_id=11,
    )

    with pytest.raises(RuntimeError, match="owner thread"):
        session.join(thread_id=12)


def test_transaction_session_join_rejects_missing_capability() -> None:
    """Join should reject nested work that needs unavailable capabilities."""
    request, staged = _build_request_and_staged()
    session = TransactionSession(
        request=request,
        staged=staged,
        owner_thread_id=11,
        capabilities=("bind",),
    )

    with pytest.raises(RuntimeError, match="required capabilities"):
        session.join(
            thread_id=11,
            required_capabilities=("contract_mutation",),
        )


def test_transaction_session_abort_pipeline_runs_hooks_then_rollbacks() -> None:
    """Abort pipeline should run hooks then reverse-order rollback actions."""
    request, staged = _build_request_and_staged()
    session = TransactionSession(
        request=request,
        staged=staged,
        owner_thread_id=11,
    )
    calls: list[str] = []

    session.register_abort_hook(lambda _staged: calls.append("abort_hook"))
    session.register_rollback_action(lambda: calls.append("rollback_1"))
    session.register_rollback_action(lambda: calls.append("rollback_2"))

    failures = session.run_abort_pipeline()

    assert failures == []
    assert calls == ["abort_hook", "rollback_2", "rollback_1"]


def test_transaction_session_commit_pipeline_runs_validator_before_hook() -> None:
    """Commit pipeline should preserve validator-before-hook ordering."""
    request, staged = _build_request_and_staged()
    session = TransactionSession(
        request=request,
        staged=staged,
        owner_thread_id=11,
    )
    calls: list[str] = []

    session.register_commit_validator(lambda _staged: calls.append("validator"))
    session.register_commit_hook(lambda _staged: calls.append("hook"))

    session.run_commit_pipeline()

    assert calls == ["validator", "hook"]
