from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError


def test_meld_execution_error_str_includes_context() -> None:
    """
    Purpose:
        Ensure MeldExecutionError string output includes contextual fields.
    Contract:
        The message includes spell identity, node, parameter, and inner exception.
    Returns:
        None.
    Raises:
        AssertionError: If the formatted message omits required context.
    """
    inner = KeyError("missing")
    error = MeldExecutionError(
        spell_id="spell-1",
        spell_name="RootSpell",
        message="resolution failed",
        node_id="node-9",
        param_name="arg",
        inner=inner,
    )

    text = str(error)
    assert "RootSpell" in text
    assert "spell-1" in text
    assert "node node-9" in text
    assert "parameter 'arg'" in text
    assert "resolution failed" in text
    assert "inner" in text
    assert "KeyError" in text
