from melder.utilities.custom_exceptions.hook_execution_error import HookExecutionError


def test_hook_execution_error_sets_details_and_message():
    original = ValueError("boom")
    err = HookExecutionError("pre_cast", "my_hook", original)

    assert err.phase == "pre_cast"
    assert err.hook_name == "my_hook"
    assert err.original_exception is original

    text = str(err)
    assert "[HOOK][pre_cast]" in text
    assert "my_hook" in text
    assert "ValueError" in text
    assert "boom" in text
