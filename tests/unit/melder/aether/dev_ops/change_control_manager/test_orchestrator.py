from threading import Event, RLock, Thread

import pytest

from melder.aether.dev_ops.change_control_manager.conflict_manager.conflict_manager import (
    ChangeControlConflictManager,
)
from melder.aether.dev_ops.change_control_manager.embargo_manager.embargo_manager import (
    ChangeControlEmbargoManager,
)
from melder.aether.dev_ops.change_control_manager.orchestrator.orchestrator import (
    ChangeControlOrchestrator,
)
from melder.aether.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
    ChangeControlTransactionManager,
)
from melder.aether.dev_ops.change_control_manager.transaction_request.transaction_request import (
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


def _build_managers():
    return (
        ChangeControlTransactionManager(),
        ChangeControlConflictManager(),
        ChangeControlEmbargoManager(),
        ChangeControlOrchestrator(),
    )


def _admit_bind_request(
    transaction_manager: ChangeControlTransactionManager,
    conflict_manager: ChangeControlConflictManager,
    embargo_manager: ChangeControlEmbargoManager,
    orchestrator: ChangeControlOrchestrator,
):
    request = transaction_manager.build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        scope_keys=["scope:spellbook:spellbook-1"],
    )
    admission = orchestrator.admit_request(
        request,
        transaction_manager=transaction_manager,
        conflict_manager=conflict_manager,
        embargo_manager=embargo_manager,
    )
    assert admission.admitted is True
    return request


def test_orchestrator_cleanup_is_idempotent_and_blocks_reuse() -> None:
    """
    Purpose:
        Validate cleanup clears staged state and forbids later use.
    Contract:
        - cleanup() is safe to call more than once.
        - Staged state and lock references are nulled after cleanup.
        - Public methods raise RuntimeError after cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup is not idempotent or reuse is allowed.
    """
    orchestrator = ChangeControlOrchestrator()
    orchestrator.cleanup()
    orchestrator.cleanup()

    assert not hasattr(orchestrator, '_staged')
    assert not hasattr(orchestrator, '_lock')

    with pytest.raises(RuntimeError):
        orchestrator.list_staged()


def test_orchestrator_cleanup_rechecks_cleaned_inside_lock() -> None:
    """
    Purpose:
        Validate the inner cleanup re-check under concurrent teardown.
    Contract:
        - A second cleanup caller may pass the outer `_cleaned` check.
        - The inner `_cleaned` check inside the lock returns safely without error.
    Returns:
        None.
    Raises:
        AssertionError: If concurrent cleanup raises or leaves the orchestrator dirty.
    """
    orchestrator = ChangeControlOrchestrator()
    orchestrator._lock = _CoordinatedLock()
    failures: list[BaseException] = []

    def _run_cleanup() -> None:
        try:
            orchestrator.cleanup()
        except BaseException as exc:
            failures.append(exc)

    first = Thread(target=_run_cleanup, name="orchestrator-cleanup-first")
    second = Thread(target=_run_cleanup, name="orchestrator-cleanup-second")

    first.start()
    assert orchestrator._lock._entered_first.wait(timeout=1.0)
    second.start()
    first.join()
    second.join()

    assert failures == []
    assert orchestrator._cleaned is True
    assert not hasattr(orchestrator, '_lock')


def test_orchestrator_accessors_handle_empty_ids_and_list_snapshot() -> None:
    """
    Purpose:
        Validate empty-id guards and staged snapshot accessors.
    Contract:
        - `get_staged(\"\")` returns None.
        - `update_staged(\"\")` returns False.
        - `list_staged()` returns a tuple snapshot of staged records.
    Returns:
        None.
    Raises:
        AssertionError: If accessor guards or snapshot behavior are incorrect.
    """
    transaction_manager, conflict_manager, embargo_manager, orchestrator = _build_managers()
    request = _admit_bind_request(
        transaction_manager,
        conflict_manager,
        embargo_manager,
        orchestrator,
    )

    assert orchestrator.get_staged("") is None
    assert orchestrator.update_staged("") is False

    staged_snapshot = orchestrator.list_staged()
    assert isinstance(staged_snapshot, tuple)
    assert len(staged_snapshot) == 1
    assert staged_snapshot[0].request_id == request.request_id


def test_orchestrator_commit_request_noops_when_request_missing() -> None:
    """
    Purpose:
        Validate commit_request returns safely for unknown request ids.
    Contract:
        - Missing in-flight requests produce a no-op.
    Returns:
        None.
    Raises:
        AssertionError: If missing requests raise or mutate state.
    """
    transaction_manager, _, embargo_manager, orchestrator = _build_managers()

    orchestrator.commit_request(
        "missing-request",
        transaction_manager=transaction_manager,
        embargo_manager=embargo_manager,
    )

    assert transaction_manager.list_in_flight() == []


def test_orchestrator_commit_request_swallows_abort_hook_failure_on_validator_error() -> None:
    """
    Purpose:
        Validate abort-hook failures are swallowed during commit rollback.
    Contract:
        - Validator failures propagate.
        - Abort-hook failures during rollback do not replace the validator error.
        - In-flight and staged state are still cleared.
    Returns:
        None.
    Raises:
        AssertionError: If rollback cleanup does not occur.
    """
    transaction_manager, conflict_manager, embargo_manager, orchestrator = _build_managers()
    request = _admit_bind_request(
        transaction_manager,
        conflict_manager,
        embargo_manager,
        orchestrator,
    )

    def _validator(_staged) -> None:
        raise RuntimeError("validation failed")

    def _abort_hook(_staged) -> None:
        raise ValueError("abort hook failed")

    orchestrator.set_commit_validator(_validator)
    orchestrator.set_abort_hook(_abort_hook)

    with pytest.raises(RuntimeError, match="validation failed"):
        orchestrator.commit_request(
            request.request_id,
            transaction_manager=transaction_manager,
            embargo_manager=embargo_manager,
        )

    assert transaction_manager.get_in_flight(request.request_id) is None
    assert orchestrator.get_staged(request.request_id) is None


def test_orchestrator_commit_request_cleans_staged_when_request_removed_in_hook() -> None:
    """
    Purpose:
        Validate commit cleanup still completes if hooks remove the in-flight request.
    Contract:
        - If a commit hook removes the request before final cleanup, staged state is
          still removed and implicit embargoes are released.
    Returns:
        None.
    Raises:
        AssertionError: If staged or embargo state leaks.
    """
    transaction_manager, conflict_manager, embargo_manager, orchestrator = _build_managers()
    request = _admit_bind_request(
        transaction_manager,
        conflict_manager,
        embargo_manager,
        orchestrator,
    )

    def _commit_hook(_staged) -> None:
        transaction_manager.remove_in_flight(request.request_id)

    orchestrator.set_commit_hook(_commit_hook)

    embargoed_before = set(embargo_manager.describe()["embargoed_scopes"])
    assert embargoed_before

    orchestrator.commit_request(
        request.request_id,
        transaction_manager=transaction_manager,
        embargo_manager=embargo_manager,
    )

    assert transaction_manager.get_in_flight(request.request_id) is None
    assert orchestrator.get_staged(request.request_id) is None
    assert embargo_manager.describe()["embargo_count"] == 0


def test_orchestrator_commit_request_failure_cleans_staged_when_request_removed() -> None:
    """
    Purpose:
        Validate failure cleanup still completes if hooks remove the in-flight request.
    Contract:
        - Validator failures still propagate.
        - If the abort hook removes the request before final cleanup, staged state
          is still removed and implicit embargoes are released.
    Returns:
        None.
    Raises:
        AssertionError: If staged or embargo state leaks.
    """
    transaction_manager, conflict_manager, embargo_manager, orchestrator = _build_managers()
    request = _admit_bind_request(
        transaction_manager,
        conflict_manager,
        embargo_manager,
        orchestrator,
    )

    def _validator(_staged) -> None:
        raise RuntimeError("validation failed")

    def _abort_hook(_staged) -> None:
        transaction_manager.remove_in_flight(request.request_id)

    orchestrator.set_commit_validator(_validator)
    orchestrator.set_abort_hook(_abort_hook)

    with pytest.raises(RuntimeError, match="validation failed"):
        orchestrator.commit_request(
            request.request_id,
            transaction_manager=transaction_manager,
            embargo_manager=embargo_manager,
        )

    assert transaction_manager.get_in_flight(request.request_id) is None
    assert orchestrator.get_staged(request.request_id) is None
    assert embargo_manager.describe()["embargo_count"] == 0


def test_orchestrator_abort_request_swallows_abort_hook_failure() -> None:
    """
    Purpose:
        Validate abort-hook failures are swallowed on abort.
    Contract:
        - Abort-hook failures do not stop in-flight/staged cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If abort cleanup does not occur.
    """
    transaction_manager, conflict_manager, embargo_manager, orchestrator = _build_managers()
    request = _admit_bind_request(
        transaction_manager,
        conflict_manager,
        embargo_manager,
        orchestrator,
    )

    def _abort_hook(_staged) -> None:
        raise ValueError("abort hook failed")

    orchestrator.set_abort_hook(_abort_hook)

    orchestrator.abort_request(
        request.request_id,
        transaction_manager=transaction_manager,
        embargo_manager=embargo_manager,
    )

    assert transaction_manager.get_in_flight(request.request_id) is None
    assert orchestrator.get_staged(request.request_id) is None


def test_orchestrator_abort_request_cleans_staged_when_request_removed_in_hook() -> None:
    """
    Purpose:
        Validate abort cleanup still completes if the abort hook removes the request.
    Contract:
        - If the abort hook removes the in-flight request before final cleanup,
          staged state is still removed and implicit embargoes are released.
    Returns:
        None.
    Raises:
        AssertionError: If staged or embargo state leaks.
    """
    transaction_manager, conflict_manager, embargo_manager, orchestrator = _build_managers()
    request = _admit_bind_request(
        transaction_manager,
        conflict_manager,
        embargo_manager,
        orchestrator,
    )

    def _abort_hook(_staged) -> None:
        transaction_manager.remove_in_flight(request.request_id)

    orchestrator.set_abort_hook(_abort_hook)

    embargoed_before = set(embargo_manager.describe()["embargoed_scopes"])
    assert embargoed_before

    orchestrator.abort_request(
        request.request_id,
        transaction_manager=transaction_manager,
        embargo_manager=embargo_manager,
    )

    assert transaction_manager.get_in_flight(request.request_id) is None
    assert orchestrator.get_staged(request.request_id) is None
    assert embargo_manager.describe()["embargo_count"] == 0


def test_orchestrator_abort_request_noops_when_request_missing() -> None:
    """
    Purpose:
        Validate abort_request returns safely for unknown request ids.
    Contract:
        - Missing in-flight requests produce a no-op.
    Returns:
        None.
    Raises:
        AssertionError: If missing requests raise or mutate state.
    """
    transaction_manager, _, embargo_manager, orchestrator = _build_managers()

    orchestrator.abort_request(
        "missing-request",
        transaction_manager=transaction_manager,
        embargo_manager=embargo_manager,
    )

    assert transaction_manager.list_in_flight() == []
