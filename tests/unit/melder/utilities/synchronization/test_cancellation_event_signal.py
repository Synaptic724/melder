import threading
import pytest

from melder.utilities.synchronization.cancellation_event_signal import (
    CancellationEvent,
    CancellationEventSignal,
)
from melder.utilities.custom_exceptions.operation_cancelled_error import OperationCancelledError


def test_cancellation_event_signals_and_clears():
    signal = CancellationEventSignal()
    evt = signal.event
    assert evt.is_set is False
    signal.cancel()
    assert evt.is_set is True
    with pytest.raises(OperationCancelledError):
        evt.throw_if_set()
    evt.cleanup()
    with pytest.raises(RuntimeError):
        _ = evt.is_set


def test_cancellation_event_signal_cleanup_disallows_use():
    signal = CancellationEventSignal()
    signal.cleanup()
    with pytest.raises(RuntimeError):
        _ = signal.event
    with pytest.raises(RuntimeError):
        signal.cancel()
    with pytest.raises(RuntimeError):
        _ = signal.is_set


def test_cancellation_event_requires_flag():
    with pytest.raises(ValueError):
        CancellationEvent(None)  # type: ignore[arg-type]


def test_cancellation_event_cleanup_is_idempotent():
    flag = threading.Event()
    evt = CancellationEvent(flag)
    evt.cleanup()
    evt.cleanup()  # no error
    with pytest.raises(RuntimeError):
        evt.throw_if_set()


def test_cancellation_event_signal_is_idempotent_cancel():
    signal = CancellationEventSignal()
    evt = signal.event
    signal.cancel()
    assert evt.is_set is True
    # multiple cancels fine
    signal.cancel()


def test_cancellation_event_signal_cleanup_cleans_child():
    signal = CancellationEventSignal()
    evt = signal.event
    signal.cleanup()
    with pytest.raises(RuntimeError):
        evt.is_set
