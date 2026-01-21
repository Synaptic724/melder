from melder.utilities.custom_exceptions.phase_timeout_error import PhaseTimeoutError
from melder.utilities.custom_exceptions.phase_scheduler_error import PhaseSchedulerError


def test_phase_timeout_error_attributes_and_message() -> None:
    """
    Purpose:
        Validate PhaseTimeoutError captures timeout metadata and message.
    Contract:
        The error inherits PhaseSchedulerError and stores phase/timeout.
    Returns:
        None.
    Raises:
        AssertionError: If attributes or message do not match expectations.
    """
    error = PhaseTimeoutError("phase-2", 1500)

    assert isinstance(error, PhaseSchedulerError)
    assert error.phase_name == "phase-2"
    assert error.timeout_ms == 1500
    assert "phase-2" in str(error)
    assert "1500 ms" in str(error)
