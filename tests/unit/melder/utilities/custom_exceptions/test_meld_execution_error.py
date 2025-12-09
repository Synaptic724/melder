from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError


def test_meld_execution_error_captures_context_and_inner():
    inner = RuntimeError("bad inner")
    err = MeldExecutionError(
        spell_id="spell-123",
        spell_name="TestSpell",
        message="failed to resolve",
        node_id="node-5",
        param_name="dependency",
        inner=inner,
    )

    assert err.spell_id == "spell-123"
    assert err.spell_name == "TestSpell"
    assert err.node_id == "node-5"
    assert err.param_name == "dependency"
    assert err.inner is inner

    text = str(err)
    assert "TestSpell" in text
    assert "spell-123" in text
    assert "node-5" in text
    assert "dependency" in text
    assert "failed to resolve" in text
    assert "RuntimeError" in text
    assert "bad inner" in text
