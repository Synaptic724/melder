import threading
from typing import Optional
from unittest.mock import MagicMock, patch

import pytest

from melder.aether.aetheric_frame.dev_ops.change_control_manager.conflict_manager.conflict_manager import (
    ChangeControlConflictManager,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.embargo_manager.embargo_manager import (
    ChangeControlEmbargoManager,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.orchestrator.orchestrator import (
    ChangeControlOrchestrator,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.orchestrator.staged_mutation import (
    ChangeControlStagedMutation,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
    ChangeControlTransactionManager,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_mediator import (
    TransactionMediator,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)
from melder.aether.aetheric_frame.dev_ops.devops_identity import DevopsIdentity
from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)


def _build_request(transaction_manager: ChangeControlTransactionManager, request_type=ChangeTransactionType.BIND):
    """Build one request for mediator tests."""
    return transaction_manager.build_request(
        request_type=request_type,
        initiator_conduit_id="conduit-1",
        spellbook_id="spellbook-1",
        scope_keys=["scope:spellbook:spellbook-1"],
    )


def _build_staged(request):
    """Build one staged mutation from a request."""
    return ChangeControlStagedMutation.from_request(
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


def _build_registry_identity(
        *,
        owner_kind: str = "spellbook",
        owner_id: str = "spellbook-1",
        metadata: Optional[dict] = None,
        available_transactions=("bind",),
):
    """Build a registry-backed identity for mediator tests."""
    registry = DevopsInformationRegistry("frame-1")
    identity = DevopsIdentity(
        owner_kind=owner_kind,
        owner_id=owner_id,
        aetheric_frame_name="frame-1",
        metadata=metadata,
        available_transactions=available_transactions,
    )
    registry.register_identity(identity)
    return registry, identity


def _build_mediator(*, registry=None, admit_request_fn=None) -> tuple[
    ChangeControlTransactionManager,
    ChangeControlConflictManager,
    ChangeControlEmbargoManager,
    ChangeControlOrchestrator,
    TransactionMediator,
]:
    """Build a mediator with fresh collaborators."""
    transaction_manager = ChangeControlTransactionManager()
    conflict_manager = ChangeControlConflictManager()
    embargo_manager = ChangeControlEmbargoManager()
    orchestrator = ChangeControlOrchestrator()
    mediator = TransactionMediator(
        transaction_manager=transaction_manager,
        conflict_manager=conflict_manager,
        embargo_manager=embargo_manager,
        orchestrator=orchestrator,
        devops_information_registry=registry,
        admit_request_fn=admit_request_fn,
    )
    return transaction_manager, conflict_manager, embargo_manager, orchestrator, mediator


def test_transaction_mediator_get_session_by_request_id_validates_type() -> None:
    """
    Purpose:
        Verify request-id lookup rejects non-string ids.
    Contract:
        - request_id must be a string.
    Returns:
        None.
    Raises:
        AssertionError: If non-string request ids are accepted.
    """
    _tm, _cm, _em, _orch, mediator = _build_mediator()

    with pytest.raises(TypeError, match="request_id must be a string."):
        mediator.get_session_by_request_id(1)


def test_transaction_mediator_get_session_by_request_id_validates_presence() -> None:
    """
    Purpose:
        Verify request-id lookup rejects empty ids.
    Contract:
        - request_id must not be empty.
    Returns:
        None.
    Raises:
        AssertionError: If empty request ids are accepted.
    """
    _tm, _cm, _em, _orch, mediator = _build_mediator()

    with pytest.raises(ValueError, match="request_id must not be empty."):
        mediator.get_session_by_request_id(" ")


def test_transaction_mediator_get_session_for_identity_returns_matching_session() -> None:
    """
    Purpose:
        Verify identity lookup returns the matching active session.
    Contract:
        - Matching owner id, owner kind, and transaction type return the session.
    Returns:
        None.
    Raises:
        AssertionError: If identity lookup misses the active session.
    """
    registry, identity = _build_registry_identity()
    transaction_manager, conflict_manager, embargo_manager, orchestrator, mediator = _build_mediator(
        registry=registry
    )
    request = _build_request(transaction_manager)
    staged = _build_staged(request)
    session = mediator.begin_frame(
        request=request,
        staged=staged,
    )
    session._submitter_identity = identity

    assert (
        mediator.get_session_for_identity(
            identity=identity,
            transaction_type="bind",
        )
        is session
    )


def test_transaction_mediator_get_session_for_identity_ignores_mismatched_type() -> None:
    """
    Purpose:
        Verify identity lookup ignores sessions with a different transaction type.
    Contract:
        - Mismatched transaction types return None.
    Returns:
        None.
    Raises:
        AssertionError: If mismatched types are treated as matches.
    """
    registry, identity = _build_registry_identity()
    transaction_manager, conflict_manager, embargo_manager, orchestrator, mediator = _build_mediator(
        registry=registry
    )
    request = _build_request(transaction_manager)
    staged = _build_staged(request)
    session = mediator.begin_frame(request=request, staged=staged)
    session._submitter_identity = identity

    assert mediator.get_session_for_identity(identity=identity, transaction_type="link") is None


def test_transaction_mediator_update_transaction_for_identity_returns_false_without_session() -> None:
    """
    Purpose:
        Verify identity-based staged updates no-op when no session is active.
    Contract:
        - Returns False instead of raising.
    Returns:
        None.
    Raises:
        AssertionError: If missing sessions raise or return True.
    """
    registry, identity = _build_registry_identity()
    _tm, _cm, _em, _orch, mediator = _build_mediator(registry=registry)

    assert (
        mediator.update_transaction_for_identity(
            identity=identity,
            transaction_type="bind",
            binding_keys=(("frame", "__default__"),),
        )
        is False
    )


def test_transaction_mediator_begin_transaction_requires_identity() -> None:
    """
    Purpose:
        Verify begin_transaction rejects missing identities.
    Contract:
        - identity must not be None.
    Returns:
        None.
    Raises:
        AssertionError: If missing identities are accepted.
    """
    _tm, _cm, _em, _orch, mediator = _build_mediator()

    with pytest.raises(ValueError, match="identity must not be None."):
        mediator.begin_transaction(
            identity=None,
            transaction_type="bind",
        )


def test_transaction_mediator_begin_transaction_rejects_unsupported_identity_transaction() -> None:
    """
    Purpose:
        Verify begin_transaction enforces identity-supported transaction kinds.
    Contract:
        - Unsupported transaction kinds raise immediately.
    Returns:
        None.
    Raises:
        AssertionError: If unsupported transaction kinds are accepted.
    """
    registry, identity = _build_registry_identity(
        available_transactions=("bind",),
    )
    _tm, _cm, _em, _orch, mediator = _build_mediator(registry=registry)

    with pytest.raises(RuntimeError, match="does not declare support"):
        mediator.begin_transaction(
            identity=identity,
            transaction_type="link",
        )


def test_transaction_mediator_begin_transaction_uses_custom_admission_function() -> None:
    """
    Purpose:
        Verify begin_transaction routes root admission through admit_request_fn.
    Contract:
        - Custom admission function is called for new root transactions.
    Returns:
        None.
    Raises:
        AssertionError: If custom admission is bypassed.
    """
    registry, identity = _build_registry_identity(metadata={"conjured": False})
    seen = []

    def _admit(request):
        seen.append(request)
        return ChangeControlOrchestrator().admit_request(
            request,
            transaction_manager=transaction_manager,
            conflict_manager=conflict_manager,
            embargo_manager=embargo_manager,
        )

    transaction_manager, conflict_manager, embargo_manager, orchestrator, mediator = _build_mediator(
        registry=registry,
        admit_request_fn=_admit,
    )

    session = mediator.begin_transaction(
        identity=identity,
        transaction_type="bind",
    )

    assert len(seen) == 1
    assert seen[0].request_type == ChangeTransactionType.BIND
    mediator.end_transaction_by_request_id(session.request.request_id, success=True)


def test_transaction_mediator_begin_transaction_same_request_id_joins_active_session() -> None:
    """
    Purpose:
        Verify begin_transaction reuses an explicit existing request id.
    Contract:
        - existing_request_id joins the active session instead of creating a new root.
    Returns:
        None.
    Raises:
        AssertionError: If explicit join creates a new root.
    """
    registry, identity = _build_registry_identity(metadata={"conjured": False})
    transaction_manager, conflict_manager, embargo_manager, orchestrator, mediator = _build_mediator(
        registry=registry
    )
    session = mediator.begin_transaction(
        identity=identity,
        transaction_type="bind",
    )

    joined = mediator.begin_transaction(
        identity=identity,
        transaction_type="bind",
        existing_request_id=session.request.request_id,
    )

    assert joined is session
    assert session.depth == 2


def test_transaction_mediator_update_transaction_for_identity_updates_staged_payload() -> None:
    """
    Purpose:
        Verify identity-based staged updates replace binding metadata on the live session.
    Contract:
        - Staged payload receives the updated binding_keys.
    Returns:
        None.
    Raises:
        AssertionError: If staged payload does not update.
    """
    registry, identity = _build_registry_identity(metadata={"conjured": False})
    transaction_manager, conflict_manager, embargo_manager, orchestrator, mediator = _build_mediator(
        registry=registry
    )
    session = mediator.begin_transaction(
        identity=identity,
        transaction_type="bind",
    )

    updated = mediator.update_transaction_for_identity(
        identity=identity,
        transaction_type="bind",
        binding_keys=(("frame", "__default__"),),
    )

    assert updated is True
    assert session.staged.binding_keys == (("frame", "__default__"),)


def test_transaction_mediator_start_transaction_rejects_unsupported_high_level_kind() -> None:
    """
    Purpose:
        Verify high-level start_transaction rejects unsupported kinds.
    Contract:
        - Unsupported high-level names raise NotImplementedError.
    Returns:
        None.
    Raises:
        AssertionError: If unsupported kinds are accepted.
    """
    registry, identity = _build_registry_identity(metadata={"conjured": False})
    _tm, _cm, _em, _orch, mediator = _build_mediator(registry=registry)

    with pytest.raises(NotImplementedError, match="not implemented"):
        mediator.start_transaction(
            identity=identity,
            transaction_type="mutation",
        )


def test_transaction_mediator_end_transaction_for_identity_rejects_missing_session() -> None:
    """
    Purpose:
        Verify identity-based end rejects when no session matches.
    Contract:
        - Missing sessions raise RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If missing sessions are silently ignored.
    """
    registry, identity = _build_registry_identity(metadata={"conjured": False})
    _tm, _cm, _em, _orch, mediator = _build_mediator(registry=registry)

    with pytest.raises(RuntimeError, match="No active transaction session exists"):
        mediator.end_transaction_for_identity(
            identity=identity,
            transaction_type="bind",
        )


def test_transaction_mediator_end_transaction_expected_type_mismatch_raises() -> None:
    """
    Purpose:
        Verify ending the active transaction enforces expected type checks.
    Contract:
        - Mismatched expected types raise RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If mismatched types are accepted.
    """
    registry, identity = _build_registry_identity(metadata={"conjured": False})
    _tm, _cm, _em, _orch, mediator = _build_mediator(registry=registry)
    mediator.begin_transaction(identity=identity, transaction_type="bind")

    with pytest.raises(RuntimeError, match="does not match the requested type"):
        mediator.end_transaction(expected_type="link")


def test_transaction_mediator_end_transaction_by_request_id_rejects_other_thread() -> None:
    """
    Purpose:
        Verify request-id end rejects non-owner threads.
    Contract:
        - Only the owner thread may end a session by request id.
    Returns:
        None.
    Raises:
        AssertionError: If other threads can end the session.
    """
    registry, identity = _build_registry_identity(metadata={"conjured": False})
    _tm, _cm, _em, _orch, mediator = _build_mediator(registry=registry)
    session = mediator.begin_transaction(identity=identity, transaction_type="bind")
    failures = []

    def _run() -> None:
        try:
            mediator.end_transaction_by_request_id(
                session.request.request_id,
                success=True,
            )
        except BaseException as exc:
            failures.append(exc)

    thread = threading.Thread(target=_run, name="mediator-end-other-thread")
    thread.start()
    thread.join(timeout=5)

    assert len(failures) == 1
    assert isinstance(failures[0], RuntimeError)
    mediator.end_transaction_by_request_id(session.request.request_id, success=True)


def test_transaction_mediator_mark_active_session_abort_only_updates_live_session() -> None:
    """
    Purpose:
        Verify mark_active_session_abort_only poisons the current session.
    Contract:
        - Active session status becomes abort_only.
        - failure_reason records the supplied message.
    Returns:
        None.
    Raises:
        AssertionError: If abort-only state is not updated.
    """
    registry, identity = _build_registry_identity(metadata={"conjured": False})
    _tm, _cm, _em, _orch, mediator = _build_mediator(registry=registry)
    session = mediator.begin_transaction(identity=identity, transaction_type="bind")

    mediator.mark_active_session_abort_only(reason="failed")

    assert session.status == session.STATUS_ABORT_ONLY
    assert session.failure_reason == "failed"
    mediator.end_transaction_by_request_id(session.request.request_id, success=False)


def test_transaction_mediator_get_active_request_returns_root_request() -> None:
    """
    Purpose:
        Verify get_active_request returns the current root request.
    Contract:
        - Active root request is returned while the session is open.
    Returns:
        None.
    Raises:
        AssertionError: If the active request is missing.
    """
    registry, identity = _build_registry_identity(metadata={"conjured": False})
    _tm, _cm, _em, _orch, mediator = _build_mediator(registry=registry)
    session = mediator.begin_transaction(identity=identity, transaction_type="bind")

    assert mediator.get_active_request() is session.request
    mediator.end_transaction_by_request_id(session.request.request_id, success=True)


def test_transaction_mediator_describe_reports_wait_bound_and_request_ids() -> None:
    """
    Purpose:
        Verify describe returns current policy and active request ids.
    Contract:
        - describe includes the scope-wait bound and the sorted request-id
          tuple.
    Returns:
        None.
    Raises:
        AssertionError: If the diagnostic snapshot is incomplete.
    """
    registry, identity = _build_registry_identity(metadata={"conjured": False})
    _tm, _cm, _em, _orch, mediator = _build_mediator(registry=registry)
    session = mediator.begin_transaction(identity=identity, transaction_type="bind")

    described = mediator.describe()

    assert described["max_transaction_wait_time_in_seconds"] == 30.0
    assert described["request_ids"] == (session.request.request_id,)
    mediator.end_transaction_by_request_id(session.request.request_id, success=True)


def test_transaction_mediator_start_strategy_transaction_reuses_same_identity_session() -> None:
    """
    Purpose:
        Verify strategy-owned starts reuse the active identity session.
    Contract:
        - Existing same-identity bind session is reused.
        - Strategy builder is not asked to build a second plan.
    Returns:
        None.
    Raises:
        AssertionError: If strategy start opens a second root.
    """
    registry, identity = _build_registry_identity(
        metadata={"conjured": False},
        available_transactions=("bind",),
    )
    _tm, _cm, _em, _orch, mediator = _build_mediator(registry=registry)
    session = mediator.begin_transaction(identity=identity, transaction_type="bind")

    class _FailingBuilder:
        """Builder fake that would fail if a new start plan were requested."""

        def build_start_plan(self, **_kwargs):
            raise AssertionError("should not build a second plan")

        def on_start(self, **_kwargs):
            return None

        def on_end(self, **_kwargs):
            return None

    mediator._strategy_builder = _FailingBuilder()
    reused = mediator._start_strategy_transaction(
        identity=identity,
        transaction_type=ChangeTransactionType.BIND,
        metadata={},
    )

    assert reused is session
    assert session.depth == 2
    mediator.end_transaction_by_request_id(session.request.request_id, success=True)


def test_transaction_mediator_start_strategy_transaction_aborts_when_on_start_fails() -> None:
    """
    Purpose:
        Verify strategy-owned starts abort when strategy on_start fails.
    Contract:
        - Failing on_start marks the session abort_only and tears it down.
        - on_end is still invoked during cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If failed strategy start leaves live session state behind.
    """
    registry, identity = _build_registry_identity(
        metadata={"conjured": False},
        available_transactions=("bind",),
    )
    _tm, _cm, _em, _orch, mediator = _build_mediator(registry=registry)

    class _ExplodingBuilder:
        """Builder fake that raises during on_start and records on_end."""

        def __init__(self) -> None:
            self.on_end_calls = 0

        def build_start_plan(self, **_kwargs):
            return {
                "initiator_conduit_id": "spellbook:spellbook-1",
                "spellbook_id": "spellbook-1",
                "conduit_ids": (),
                "scope_keys": ("scope:spellbook:spellbook-1",),
                "scope_hashes": (),
                "binding_keys": (),
                "contract_keys": (),
                "granted_capabilities": ("bind",),
                "required_capabilities": ("bind",),
                "metadata": {},
            }

        def on_start(self, **_kwargs):
            raise RuntimeError("boom")

        def on_end(self, **_kwargs):
            self.on_end_calls += 1

    builder = _ExplodingBuilder()
    mediator._strategy_builder = builder

    with pytest.raises(RuntimeError, match="boom"):
        mediator._start_strategy_transaction(
            identity=identity,
            transaction_type=ChangeTransactionType.BIND,
            metadata={},
        )

    assert mediator.describe()["active_session_count"] == 0
    assert builder.on_end_calls == 1
