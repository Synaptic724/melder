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
