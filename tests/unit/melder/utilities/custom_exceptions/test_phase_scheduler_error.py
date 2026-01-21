from melder.utilities.custom_exceptions.phase_scheduler_error import PhaseSchedulerError


def test_phase_scheduler_error_preserves_message() -> None:
    """
    Purpose:
        Confirm PhaseSchedulerError keeps the provided message.
    Contract:
        The error is a RuntimeError with the same string payload.
    Returns:
        None.
    Raises:
        AssertionError: If the message is not preserved.
    """
    error = PhaseSchedulerError("scheduler failed")
    assert isinstance(error, RuntimeError)
    assert str(error) == "scheduler failed"
