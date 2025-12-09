import pytest

from melder.utilities.custom_exceptions.phase_execution_error import PhaseExecutionError
from melder.utilities.custom_exceptions.phase_scheduler_error import PhaseSchedulerError


def test_phase_execution_error_includes_phase_and_errors():
    errors = [ValueError("oops"), RuntimeError("boom")]
    err = PhaseExecutionError("bootstrap", errors)

    assert isinstance(err, PhaseSchedulerError)
    assert err.phase_name == "bootstrap"
    assert err.errors == errors

    text = str(err)
    assert "bootstrap" in text
    assert "2 error(s)" in text


def test_phase_execution_error_raises():
    with pytest.raises(PhaseExecutionError):
        raise PhaseExecutionError("phase", [])
