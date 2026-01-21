from melder.utilities.custom_exceptions.empty_error import Empty


def test_empty_error_inherits_exception_and_preserves_message() -> None:
    """
    Purpose:
        Confirm Empty is an Exception subclass with a preserved message.
    Contract:
        The error instance is an Exception and echoes the message string.
    Returns:
        None.
    Raises:
        AssertionError: If inheritance or message does not match.
    """
    error = Empty("container empty")
    assert isinstance(error, Exception)
    assert str(error) == "container empty"
