from melder.utilities.custom_exceptions.phase_execution_error import PhaseExecutionError
from melder.utilities.custom_exceptions.phase_scheduler_error import PhaseSchedulerError


def test_phase_execution_error_message_and_fields() -> None:
    """
    Purpose:
        Validate PhaseExecutionError captures phase and error list.
    Contract:
        The error is a PhaseSchedulerError with phase metadata and count.
    Returns:
        None.
    Raises:
        AssertionError: If attributes or message are incorrect.
    """
    errors = [ValueError("a"), RuntimeError("b")]
    error = PhaseExecutionError("phase-1", errors)

    assert isinstance(error, PhaseSchedulerError)
    assert error.phase_name == "phase-1"
    assert error.errors == errors
    assert "2 error(s)" in str(error)
