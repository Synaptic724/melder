import pytest

from melder.utilities.custom_exceptions.phase_scheduler_error import PhaseSchedulerError


def test_phase_scheduler_error_is_runtime_error_and_preserves_message():
    err = PhaseSchedulerError("scheduler broke")
    assert isinstance(err, RuntimeError)
    assert str(err) == "scheduler broke"


def test_phase_scheduler_error_raises():
    with pytest.raises(PhaseSchedulerError):
        raise PhaseSchedulerError("fail")
