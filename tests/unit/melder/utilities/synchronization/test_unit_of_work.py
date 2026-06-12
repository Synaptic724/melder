import threading
import time

import pytest

from melder.utilities.synchronization.unit_of_work import UnitOfWork
from melder.utilities.synchronization.cancellation_event_signal import (
    CancellationEventSignal,
    CancellationEvent,
)
from melder.utilities.custom_exceptions.operation_cancelled_error import OperationCancelledError


def test_init_rejects_non_callable():
    with pytest.raises(TypeError):
        UnitOfWork(func=123)  # type: ignore[arg-type]


def test_run_synchronously_success_sets_result_and_done():
    uow = UnitOfWork(lambda: 5)
    result = uow.run_synchronously()
    assert result == 5
    assert uow.done() is True
    assert uow.result() == 5
    assert uow.exception() is None


def test_run_synchronously_exception_propagates_and_records():
    err = RuntimeError("boom")
    uow = UnitOfWork(lambda: (_ for _ in ()).throw(err))
    with pytest.raises(RuntimeError):
        uow.run_synchronously()
    assert uow.done() is True
    assert isinstance(uow.exception(), RuntimeError)


def test_run_synchronously_honors_cancel_event():
    signal = CancellationEventSignal()
    signal.cancel()
    uow = UnitOfWork(lambda: 1, cancel_event=signal.event)
    with pytest.raises(OperationCancelledError):
        uow.run_synchronously()
    assert uow.done() is True
    assert isinstance(uow.exception(), OperationCancelledError)


def test_call_alias_invokes_run():
    called = []

    def _fn():
        called.append(1)
        return "ok"

    uow = UnitOfWork(_fn)
    assert uow() == "ok"
    assert called == [1]
    assert uow.result() == "ok"


def test_second_run_returns_cached_result_without_rerun():
    counter = {"n": 0}

    def _fn():
        counter["n"] += 1
        return counter["n"]

    uow = UnitOfWork(_fn)
    assert uow.run_synchronously() == 1
    # second run should not call _fn again
    assert uow.run_synchronously() == 1
    assert counter["n"] == 1


def test_properties_expose_metadata_and_label():
    sig = CancellationEventSignal()
    uow = UnitOfWork(lambda: None, label="L", metadata={"a": 1}, cancel_event=sig.event)
    assert isinstance(uow.cancel_event, CancellationEvent)
    assert uow.label == "L"
    assert uow.metadata == {"a": 1}


def test_context_manager_locks_and_unlocks():
    uow = UnitOfWork(lambda: None)
    # ensure lock held during context and released afterwards
    with uow:
        # lock is re-entrant; count increases when acquired again
        assert uow._lock.acquire(blocking=False) is True
        uow._lock.release()
    # after context, lock is free
    assert uow._lock.acquire(blocking=False) is True
    uow._lock.release()


def test_cleanup_idempotent_and_nulls_references():
    uow = UnitOfWork(lambda: 1, args=(1,), kwargs={"x": 2}, label="lbl", metadata="m")
    uow.cleanup()
    uow.cleanup()
    assert not hasattr(uow, '_func')
    assert not hasattr(uow, '_args')
    assert not hasattr(uow, '_kwargs')
    assert not hasattr(uow, '_cancel_event')
    assert not hasattr(uow, '_label')
    assert not hasattr(uow, '_metadata')
    with pytest.raises(RuntimeError):
        uow.run_synchronously()
    with pytest.raises(RuntimeError):
        _ = uow.cancel_event


def test_run_after_cleanup_raises():
    uow = UnitOfWork(lambda: 1)
    uow.cleanup()
    with pytest.raises(RuntimeError):
        uow()


def test_run_with_args_and_kwargs():
    uow = UnitOfWork(lambda a, b=0: a + b, args=(2,), kwargs={"b": 3})
    assert uow.run_synchronously() == 5


def test_metadata_and_label_after_cleanup_raise():
    uow = UnitOfWork(lambda: None, label="lab", metadata="meta")
    uow.cleanup()
    with pytest.raises(RuntimeError):
        _ = uow.label
    with pytest.raises(RuntimeError):
        _ = uow.metadata


def test_operation_cancelled_error_contains_label():
    sig = CancellationEventSignal()
    uow = UnitOfWork(lambda: None, label="X", cancel_event=sig.event)
    sig.cancel()
    with pytest.raises(OperationCancelledError) as excinfo:
        uow.run_synchronously()
    assert "X" in str(excinfo.value)


def test_exception_recorded_on_future_when_function_raises():
    uow = UnitOfWork(lambda: 1 / 0)
    with pytest.raises(ZeroDivisionError):
        uow.run_synchronously()
    assert isinstance(uow.exception(), ZeroDivisionError)


def test_thread_safety_basic_lock_usage():
    # Verify that concurrent acquisitions respect the lock
    uow = UnitOfWork(lambda: time.sleep(0.05))

    acquired_in_thread = []
    entered = threading.Event()

    def worker():
        with uow:
            acquired_in_thread.append(True)
            entered.set()
            time.sleep(0.05)

    t = threading.Thread(target=worker)
    t.start()
    # Wait for thread to acquire lock
    entered.wait(timeout=0.1)
    assert uow._lock.acquire(blocking=False) is False
    t.join(timeout=5)
    assert acquired_in_thread == [True]
    # Lock is released after context
    assert uow._lock.acquire(blocking=False) is True
    uow._lock.release()


def test_done_and_result_behaviour_matches_future():
    uow = UnitOfWork(lambda: 10)
    assert uow.done() is False
    uow.run_synchronously()
    assert uow.done() is True
    assert uow.result() == 10


def test_exception_is_preserved_on_future():
    uow = UnitOfWork(lambda: (_ for _ in ()).throw(ValueError("bad")))
    with pytest.raises(ValueError):
        uow.run_synchronously()
    assert isinstance(uow.exception(), ValueError)


def test_cancel_event_throw_if_set_integration():
    signal = CancellationEventSignal()
    event = signal.event
    signal.cancel()
    with pytest.raises(OperationCancelledError):
        event.throw_if_set()


def test_run_for_scheduler_success_records_result_and_returns_none():
    uow = UnitOfWork(lambda: 7)
    failure = uow.run_for_scheduler()
    assert failure is None
    assert uow.done() is True
    assert uow.result() == 7


def test_run_for_scheduler_failure_returns_exception_without_raising():
    err = ValueError("bad")
    uow = UnitOfWork(lambda: (_ for _ in ()).throw(err))
    failure = uow.run_for_scheduler()
    assert failure is err
    assert isinstance(uow.exception(), ValueError)


def test_run_for_scheduler_cancelled_returns_cancellation_without_running():
    signal = CancellationEventSignal()
    signal.cancel()
    counter = {"n": 0}

    def _fn():
        counter["n"] += 1

    uow = UnitOfWork(_fn, cancel_event=signal.event, label="C")
    failure = uow.run_for_scheduler()
    assert isinstance(failure, OperationCancelledError)
    assert "C" in str(failure)
    assert counter["n"] == 0
    assert isinstance(uow.exception(), OperationCancelledError)


def test_run_for_scheduler_skips_already_done_unit():
    counter = {"n": 0}

    def _fn():
        counter["n"] += 1
        return counter["n"]

    uow = UnitOfWork(_fn)
    uow.run_synchronously()
    failure = uow.run_for_scheduler()
    assert failure is None
    assert counter["n"] == 1
    assert uow.result() == 1


def test_run_for_scheduler_control_thread_abort_outcome_wins():
    # A barrier abort (control-thread set_exception) decided this unit's
    # outcome; the worker's late execution must not overwrite or raise.
    uow = UnitOfWork(lambda: "late")
    abort = OperationCancelledError("aborted by barrier")
    uow.set_exception(abort)
    failure = uow.run_for_scheduler()
    assert failure is None
    assert uow.exception() is abort


def test_run_for_scheduler_on_cleaned_unit_is_noop():
    uow = UnitOfWork(lambda: 1)
    uow.cleanup()
    assert uow.run_for_scheduler() is None
