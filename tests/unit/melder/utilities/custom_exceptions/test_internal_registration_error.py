from melder.utilities.custom_exceptions.internal_registration_error import (
    InternalRegistrationError,
)


def test_internal_registration_error_inherits_runtime_error_and_preserves_message() -> None:
    """
    Purpose:
        Verify InternalRegistrationError is a RuntimeError subclass with stable
        default Exception message behavior.
    Contract:
        - The error remains catchable as RuntimeError.
        - The provided message is preserved unchanged.
    Returns:
        None.
    Raises:
        AssertionError: If the type hierarchy or message is incorrect.
    """
    error = InternalRegistrationError("framework-owned sentinel")

    assert isinstance(error, RuntimeError)
    assert str(error) == "framework-owned sentinel"
