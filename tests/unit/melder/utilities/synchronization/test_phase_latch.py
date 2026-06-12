import threading

import pytest

from melder.utilities.synchronization.phase_latch import PhaseLatch


def test_ctor_rejects_non_positive_and_bool_counts():
    with pytest.raises(ValueError):
        PhaseLatch(0)
    with pytest.raises(ValueError):
        PhaseLatch(-1)
    with pytest.raises(ValueError):
        PhaseLatch(True)
    with pytest.raises(ValueError):
        PhaseLatch("3")  # type: ignore[arg-type]


def test_all_completions_fire_event():
    latch = PhaseLatch(3)
    latch.complete()
    latch.complete()
    assert latch.wait(0.0) is False
    latch.complete()
    assert latch.wait(0.0) is True
    assert latch.errors == []


def test_record_error_fires_event_immediately_and_counts_completion():
    latch = PhaseLatch(3)
    err = RuntimeError("boom")
    latch.record_error(err)
    # Fail-fast: the event fires before the remaining units report.
    assert latch.wait(0.0) is True
    assert latch.errors == [err]


def test_wait_times_out_when_units_missing():
    latch = PhaseLatch(2)
    latch.complete()
    assert latch.wait(0.01) is False


def test_late_completions_after_fail_fast_are_harmless():
    latch = PhaseLatch(2)
    latch.record_error(ValueError("first"))
    # Straggler reports after the fail-fast wake; counter may pass zero.
    latch.complete()
    assert latch.wait(0.0) is True
    assert len(latch.errors) == 1


def test_errors_property_returns_snapshot_copy():
    latch = PhaseLatch(2)
    err = RuntimeError("x")
    latch.record_error(err)
    snapshot = latch.errors
    snapshot.append(RuntimeError("injected"))
    assert latch.errors == [err]


def test_cross_thread_completion_wakes_waiter():
    latch = PhaseLatch(1)

    def _worker() -> None:
        latch.complete()

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    assert latch.wait(2.0) is True
    thread.join(timeout=2.0)
