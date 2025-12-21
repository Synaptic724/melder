from melder.utilities.custom_exceptions.operation_cancelled_error import OperationCancelledError


def test_operation_cancelled_error_inherits_runtimeerror() -> None:
    """
    Purpose:
        Confirm OperationCancelledError is a RuntimeError subclass.
    Contract:
        The error preserves the provided message.
    Returns:
        None.
    Raises:
        AssertionError: If inheritance or message does not match.
    """
    error = OperationCancelledError("cancelled")
    assert isinstance(error, RuntimeError)
    assert str(error) == "cancelled"
