from melder.utilities.custom_exceptions.hook_execution_error import HookExecutionError


def test_hook_execution_error_formats_message_and_attributes() -> None:
    """
    Purpose:
        Validate HookExecutionError captures phase metadata and formats message.
    Contract:
        The error stores phase, hook name, and original exception.
    Returns:
        None.
    Raises:
        AssertionError: If attributes or message formatting are incorrect.
    """
    original = ValueError("boom")
    error = HookExecutionError("activation", "hook_fn", original)

    assert error.phase == "activation"
    assert error.hook_name == "hook_fn"
    assert error.original_exception is original
    assert "[HOOK][activation]" in str(error)
    assert "hook_fn" in str(error)
    assert "ValueError" in str(error)
    assert "boom" in str(error)
