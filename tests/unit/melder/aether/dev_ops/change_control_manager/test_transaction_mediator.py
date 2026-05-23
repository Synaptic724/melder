import threading
import time
import warnings

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


def _build_admitted_bundle():
    """Build one admitted request bundle for mediator tests."""
    transaction_manager = ChangeControlTransactionManager()
    conflict_manager = ChangeControlConflictManager()
    embargo_manager = ChangeControlEmbargoManager()
    orchestrator = ChangeControlOrchestrator()
    request = transaction_manager.build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        spellbook_id="spellbook-1",
        scope_keys=["scope:spellbook:spellbook-1"],
    )
    admission = orchestrator.admit_request(
        request,
        transaction_manager=transaction_manager,
        conflict_manager=conflict_manager,
        embargo_manager=embargo_manager,
    )
    assert admission.admitted is True
    staged = orchestrator.get_staged(request.request_id)
    assert staged is not None
    mediator = TransactionMediator(
        transaction_manager=transaction_manager,
        conflict_manager=conflict_manager,
        embargo_manager=embargo_manager,
        orchestrator=orchestrator,
        devops_information_registry=None,
    )
    return transaction_manager, embargo_manager, orchestrator, request, staged, mediator


def test_transaction_mediator_begin_root_session_tracks_active_session() -> None:
    """Root begin should create one active session for the current thread."""
    _tm, _em, _orch, request, staged, mediator = _build_admitted_bundle()

    session = mediator.begin_frame(
        request=request,
        staged=staged,
        capabilities=("bind",),
    )

    assert session.request is request
    assert mediator.has_active_session() is True
    assert mediator.get_active_session() is session
    assert mediator.describe()["active_session_count"] == 1


def test_transaction_mediator_same_thread_join_reuses_root_session() -> None:
    """Nested same-thread begin should reuse the same root session."""
    _tm, _em, _orch, request, staged, mediator = _build_admitted_bundle()
    session = mediator.begin_frame(
        request=request,
        staged=staged,
        capabilities=("contract_mutation",),
    )

    joined = mediator.begin_frame(required_capabilities=("contract_mutation",))

    assert joined is session
    assert session.depth == 2


def test_transaction_mediator_strict_mode_rejects_cross_thread_root_begin() -> None:
    """Strict mode should reject a second root session from another thread."""
    _tm, _em, _orch, request, staged, mediator = _build_admitted_bundle()
    mediator.begin_frame(request=request, staged=staged)

    other_request = _tm.build_request(
        request_type=ChangeTransactionType.LINK,
        initiator_conduit_id="conduit-2",
        spellbook_id="spellbook-2",
        scope_keys=["scope:spellbook:spellbook-2"],
    )
    other_staged = ChangeControlStagedMutation.from_request(
        request_id=other_request.request_id,
        request_type=other_request.request_type,
        initiator_conduit_id=other_request.initiator_conduit_id,
        spellbook_id=other_request.spellbook_id,
        conduit_ids=other_request.conduit_ids,
        scope_keys=other_request.scope_keys,
        binding_keys=other_request.binding_keys,
        contract_keys=other_request.contract_keys,
        metadata=other_request.metadata,
    )

    failures: list[BaseException] = []

    def _run() -> None:
        try:
            mediator.begin_frame(request=other_request, staged=other_staged)
        except BaseException as exc:
            failures.append(exc)

    thread = threading.Thread(target=_run, name="mediator-strict")
    thread.start()
    thread.join(timeout=5)
    assert thread.is_alive() is False
    assert len(failures) == 1
    assert isinstance(failures[0], RuntimeError)


def test_transaction_mediator_warn_mode_allows_cross_thread_root_begin() -> None:
    """Warn mode should allow a second root session and emit one warning."""
    _tm, _em, _orch, request, staged, mediator = _build_admitted_bundle()
    mediator.begin_frame(request=request, staged=staged)
    mediator.configure(
        change_control_mode="warn",
        allow_multiple_root_transactions=False,
        queue_competing_root_transactions=False,
        max_transaction_wait_time_in_seconds=30.0,
    )

    other_request = _tm.build_request(
        request_type=ChangeTransactionType.LINK,
        initiator_conduit_id="conduit-2",
        spellbook_id="spellbook-2",
        scope_keys=["scope:spellbook:spellbook-2"],
    )
    other_staged = ChangeControlStagedMutation.from_request(
        request_id=other_request.request_id,
        request_type=other_request.request_type,
        initiator_conduit_id=other_request.initiator_conduit_id,
        spellbook_id=other_request.spellbook_id,
        conduit_ids=other_request.conduit_ids,
        scope_keys=other_request.scope_keys,
        binding_keys=other_request.binding_keys,
        contract_keys=other_request.contract_keys,
        metadata=other_request.metadata,
    )

    captured: list[warnings.WarningMessage] = []

    def _run() -> None:
        with warnings.catch_warnings(record=True) as seen:
            warnings.simplefilter("always")
            mediator.begin_frame(request=other_request, staged=other_staged)
            captured.extend(seen)

    thread = threading.Thread(target=_run, name="mediator-warn")
    thread.start()
    thread.join(timeout=5)
    assert thread.is_alive() is False
    assert captured
    assert mediator.describe()["active_session_count"] == 2


def test_transaction_mediator_queue_waits_then_allows_next_root_start() -> None:
    """Queued mode should let a competing thread begin after the root finishes."""
    _tm, _em, _orch, request, staged, mediator = _build_admitted_bundle()
    mediator.configure(
        change_control_mode="strict",
        allow_multiple_root_transactions=False,
        queue_competing_root_transactions=True,
        max_transaction_wait_time_in_seconds=1.0,
    )
    mediator.begin_frame(request=request, staged=staged)

    other_request = _tm.build_request(
        request_type=ChangeTransactionType.LINK,
        initiator_conduit_id="conduit-2",
        spellbook_id="spellbook-2",
        scope_keys=["scope:spellbook:spellbook-2"],
    )
    other_staged = ChangeControlStagedMutation.from_request(
        request_id=other_request.request_id,
        request_type=other_request.request_type,
        initiator_conduit_id=other_request.initiator_conduit_id,
        spellbook_id=other_request.spellbook_id,
        conduit_ids=other_request.conduit_ids,
        scope_keys=other_request.scope_keys,
        binding_keys=other_request.binding_keys,
        contract_keys=other_request.contract_keys,
        metadata=other_request.metadata,
    )

    finished = threading.Event()
    failures: list[BaseException] = []

    def _run() -> None:
        try:
            session = mediator.begin_frame(request=other_request, staged=other_staged)
            assert session.request is other_request
            mediator.end_frame(success=True)
        except BaseException as exc:
            failures.append(exc)
        finally:
            finished.set()

    thread = threading.Thread(target=_run, name="mediator-queued")
    thread.start()
    assert finished.wait(timeout=0.05) is False
    mediator.end_frame(success=True)
    assert finished.wait(timeout=1.0) is True
    thread.join(timeout=5)
    assert thread.is_alive() is False
    assert failures == []


def test_transaction_mediator_queue_times_out_when_root_never_finishes() -> None:
    """Queued mode should time out if the active root session never ends."""
    _tm, _em, _orch, request, staged, mediator = _build_admitted_bundle()
    mediator.configure(
        change_control_mode="strict",
        allow_multiple_root_transactions=False,
        queue_competing_root_transactions=True,
        max_transaction_wait_time_in_seconds=0.05,
    )
    mediator.begin_frame(request=request, staged=staged)

    other_request = _tm.build_request(
        request_type=ChangeTransactionType.LINK,
        initiator_conduit_id="conduit-2",
        spellbook_id="spellbook-2",
        scope_keys=["scope:spellbook:spellbook-2"],
    )
    other_staged = ChangeControlStagedMutation.from_request(
        request_id=other_request.request_id,
        request_type=other_request.request_type,
        initiator_conduit_id=other_request.initiator_conduit_id,
        spellbook_id=other_request.spellbook_id,
        conduit_ids=other_request.conduit_ids,
        scope_keys=other_request.scope_keys,
        binding_keys=other_request.binding_keys,
        contract_keys=other_request.contract_keys,
        metadata=other_request.metadata,
    )

    failures: list[BaseException] = []

    def _run() -> None:
        try:
            mediator.begin_frame(request=other_request, staged=other_staged)
        except BaseException as exc:
            failures.append(exc)

    thread = threading.Thread(target=_run, name="mediator-timeout")
    thread.start()
    thread.join(timeout=5)
    assert thread.is_alive() is False
    assert len(failures) == 1
    assert isinstance(failures[0], RuntimeError)
    assert "Timed out waiting" in str(failures[0])


def test_transaction_mediator_queue_drains_five_waiters_one_by_one_in_fifo_order() -> None:
    """Queued mode should drain five waiting root starts one by one in FIFO order."""
    _tm, _em, _orch, request, staged, mediator = _build_admitted_bundle()
    mediator.configure(
        change_control_mode="strict",
        allow_multiple_root_transactions=False,
        queue_competing_root_transactions=True,
        max_transaction_wait_time_in_seconds=1.0,
    )
    mediator.begin_frame(request=request, staged=staged)

    worker_payloads = []
    for idx in range(5):
        req = _tm.build_request(
            request_type=ChangeTransactionType.LINK,
            initiator_conduit_id=f"conduit-{idx + 2}",
            spellbook_id=f"spellbook-{idx + 2}",
            scope_keys=[f"scope:spellbook:spellbook-{idx + 2}"],
        )
        staged_req = ChangeControlStagedMutation.from_request(
            request_id=req.request_id,
            request_type=req.request_type,
            initiator_conduit_id=req.initiator_conduit_id,
            spellbook_id=req.spellbook_id,
            conduit_ids=req.conduit_ids,
            scope_keys=req.scope_keys,
            binding_keys=req.binding_keys,
            contract_keys=req.contract_keys,
            metadata=req.metadata,
        )
        worker_payloads.append((idx, req, staged_req))

    acquisition_order: list[int] = []
    failures: list[BaseException] = []
    active_count = 0
    max_active = 0
    state_lock = threading.Lock()
    finished_events = [threading.Event() for _ in range(5)]

    def _run(index: int, req, staged_req, finished: threading.Event) -> None:
        nonlocal active_count, max_active
        try:
            session = mediator.begin_frame(request=req, staged=staged_req)
            with state_lock:
                acquisition_order.append(index)
                active_count += 1
                max_active = max(max_active, active_count)
            time.sleep(0.02)
            with state_lock:
                active_count -= 1
            mediator.end_frame(success=True)
            assert session.request is req
        except BaseException as exc:
            failures.append(exc)
        finally:
            finished.set()

    threads = []
    for idx, req, staged_req in worker_payloads:
        finished = finished_events[idx]
        thread = threading.Thread(
            target=_run,
            args=(idx, req, staged_req, finished),
            name=f"mediator-queued-five-{idx}",
        )
        thread.start()
        threads.append(thread)
        deadline = time.monotonic() + 1.0
        while True:
            with mediator._lock:  # unit-test-only internal check to confirm queue ordering
                pending_count = len(mediator._pending_root_starts)
            if pending_count >= idx + 1:
                break
            if time.monotonic() >= deadline:
                raise AssertionError("Worker did not enter the pending-start queue in time.")
            time.sleep(0.005)

    assert all(event.wait(timeout=0.05) is False for event in finished_events)
    mediator.end_frame(success=True)
    for thread in threads:
        thread.join(timeout=5)
        assert thread.is_alive() is False

    assert failures == []
    assert acquisition_order == [0, 1, 2, 3, 4]
    assert max_active == 1


def test_transaction_mediator_root_success_commits_and_clears_session() -> None:
    """Outermost success should commit and clear active session state."""
    transaction_manager, _embargo_manager, orchestrator, request, staged, mediator = _build_admitted_bundle()

    session = mediator.begin_frame(request=request, staged=staged)
    mediator.end_frame(success=True)

    assert session.status == session.STATUS_COMMITTED
    assert transaction_manager.get_in_flight(request.request_id) is None
    assert orchestrator.get_staged(request.request_id) is None
    assert mediator.has_active_session() is False


def test_transaction_mediator_root_failure_aborts_and_clears_session() -> None:
    """Outermost failure should abort and clear active session state."""
    transaction_manager, _embargo_manager, orchestrator, request, staged, mediator = _build_admitted_bundle()

    session = mediator.begin_frame(request=request, staged=staged)
    mediator.end_frame(success=False)

    assert session.status == session.STATUS_ABORTED
    assert transaction_manager.get_in_flight(request.request_id) is None
    assert orchestrator.get_staged(request.request_id) is None
    assert mediator.has_active_session() is False
