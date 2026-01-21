from melder.utilities.custom_exceptions.spell_space_scope_error import SpellSpaceScopeError


def test_spell_space_scope_error_preserves_message() -> None:
    """
    Purpose:
        Confirm SpellSpaceScopeError is a RuntimeError with message preserved.
    Contract:
        The error instance is a RuntimeError and echoes the message.
    Returns:
        None.
    Raises:
        AssertionError: If type or message is incorrect.
    """
    error = SpellSpaceScopeError("missing spell space")
    assert isinstance(error, RuntimeError)
    assert str(error) == "missing spell space"
