import pytest

from melder.utilities.custom_exceptions.phase_scheduler_error import PhaseSchedulerError
from melder.utilities.custom_exceptions.phase_timeout_error import PhaseTimeoutError


def test_phase_timeout_error_sets_fields_and_message():
    err = PhaseTimeoutError("validation", 2500)

    assert isinstance(err, PhaseSchedulerError)
    assert err.phase_name == "validation"
    assert err.timeout_ms == 2500

    text = str(err)
    assert "validation" in text
    assert "2500" in text


def test_phase_timeout_error_raises():
    with pytest.raises(PhaseTimeoutError):
        raise PhaseTimeoutError("phase", 1)
