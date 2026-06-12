import threading
import time
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


def test_transaction_mediator_allows_cross_thread_root_begin_by_default() -> None:
    """Cross-thread root begin should be allowed by default when queueing is off."""
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
    sessions = []

    def _run() -> None:
        try:
            sessions.append(
                mediator.begin_frame(request=other_request, staged=other_staged)
            )
        except BaseException as exc:
            failures.append(exc)

    thread = threading.Thread(target=_run, name="mediator-parallel-default")
    thread.start()
    thread.join(timeout=5)
    assert thread.is_alive() is False
    assert failures == []
    assert mediator.describe()["active_session_count"] == 2


def test_transaction_mediator_deprecated_queue_flag_does_not_block_cross_thread_roots() -> None:
    """The deprecated queue flag must not delay disjoint cross-thread root starts.

    Root arbitration is scope-driven under the acquisition contract; `begin_frame`
    hosts pre-admitted requests, so a competing thread proceeds immediately even
    while another root session is active and the legacy flag is set.
    """
    _tm, _em, _orch, request, staged, mediator = _build_admitted_bundle()
    mediator.configure(
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

    thread = threading.Thread(target=_run, name="mediator-disjoint-root")
    thread.start()
    assert finished.wait(timeout=1.0) is True
    thread.join(timeout=5)
    assert thread.is_alive() is False
    assert failures == []
    mediator.end_frame(success=True)


def test_transaction_mediator_deprecated_queue_flag_never_times_out_root_starts() -> None:
    """The deprecated queue flag must not impose FIFO timeouts on root starts.

    Pre-acquisition timeouts belong to scope waiting only; a disjoint root start
    completes even when another root session never finishes and the legacy flag
    plus a tiny wait bound are configured.
    """
    _tm, _em, _orch, request, staged, mediator = _build_admitted_bundle()
    mediator.configure(
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
    completed = threading.Event()

    def _run() -> None:
        try:
            mediator.begin_frame(request=other_request, staged=other_staged)
            mediator.end_frame(success=True)
            completed.set()
        except BaseException as exc:
            failures.append(exc)

    thread = threading.Thread(target=_run, name="mediator-no-timeout")
    thread.start()
    thread.join(timeout=5)
    assert thread.is_alive() is False
    assert failures == []
    assert completed.is_set()
    mediator.end_frame(success=True)


def test_transaction_mediator_concurrent_disjoint_root_starts_proceed_without_fifo() -> None:
    """Disjoint cross-thread root starts proceed concurrently with no FIFO drain.

    Five workers host pre-admitted disjoint requests while one root session is
    already active; all complete without waiting on each other because overlap,
    not arrival order, is the only serialization criterion.
    """
    _tm, _em, _orch, request, staged, mediator = _build_admitted_bundle()
    mediator.configure(
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

    completion_order: list[int] = []
    failures: list[BaseException] = []
    state_lock = threading.Lock()
    finished_events = [threading.Event() for _ in range(5)]

    def _run(index: int, req, staged_req, finished: threading.Event) -> None:
        try:
            session = mediator.begin_frame(request=req, staged=staged_req)
            time.sleep(0.02)
            mediator.end_frame(success=True)
            assert session.request is req
            with state_lock:
                completion_order.append(index)
        except BaseException as exc:
            failures.append(exc)
        finally:
            finished.set()

    threads = []
    for idx, req, staged_req in worker_payloads:
        thread = threading.Thread(
            target=_run,
            args=(idx, req, staged_req, finished_events[idx]),
            name=f"mediator-disjoint-five-{idx}",
        )
        thread.start()
        threads.append(thread)

    for event in finished_events:
        assert event.wait(timeout=5.0) is True
    for thread in threads:
        thread.join(timeout=5)
        assert thread.is_alive() is False

    assert failures == []
    assert sorted(completion_order) == [0, 1, 2, 3, 4]
    mediator.end_frame(success=True)


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
