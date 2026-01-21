from melder.utilities.custom_exceptions.dead_reference_error import DeadReferenceError


def test_dead_reference_error_inherits_reference_error() -> None:
    """
    Purpose:
        Verify DeadReferenceError is a ReferenceError subclass.
    Contract:
        The error preserves the provided message.
    Returns:
        None.
    Raises:
        AssertionError: If the type or message is incorrect.
    """
    error = DeadReferenceError("missing target")
    assert isinstance(error, ReferenceError)
    assert str(error) == "missing target"
