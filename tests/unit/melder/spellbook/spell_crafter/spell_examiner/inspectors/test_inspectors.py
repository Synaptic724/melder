from melder.spellbook.spell_crafter.spell_examiner.inspectors.inspector_utility import (
    InspectorUtility,
)
from melder.spellbook.spell_crafter.spell_examiner.inspectors.method_inspector import (
    MethodInspector,
)


def _original_function(value: int, other: int = 1) -> int:
    """
    Purpose:
        Provide a stable callable for inspector tests.
    Contract:
        Returns the sum of value and other.
    Args:
        value: Primary input value.
        other: Optional addend.
    Returns:
        int: Sum of value and other.
    """
    return value + other


def _simple_decorator(fn):
    """
    Purpose:
        Create a wrapper without functools.wraps for unwrapping tests.
    Contract:
        Returns a callable that delegates to the wrapped function.
    Args:
        fn: Callable to wrap.
    Returns:
        callable: Wrapper that forwards all arguments.
    """
    def _wrapper(*args, **kwargs):
        """
        Purpose:
            Delegate calls to the wrapped function.
        Contract:
            Returns the wrapped function's result.
        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.
        Returns:
            object: Result from the wrapped function.
        """
        return fn(*args, **kwargs)

    return _wrapper


class _ReprBoom:
    """
    Purpose:
        Provide an object whose repr raises for safe_repr testing.
    Contract:
        __repr__ always raises RuntimeError.
    """
    def __repr__(self) -> str:
        """
        Purpose:
            Simulate a failing repr implementation.
        Contract:
            Always raises RuntimeError.
        Returns:
            str: Never returned.
        Raises:
            RuntimeError: Always raised to test fallback behavior.
        """
        raise RuntimeError("boom")


def test_safe_repr_truncates_long_string() -> None:
    """
    Purpose:
        Validate safe_repr truncates long representations.
    Contract:
        Truncated output includes ellipsis and original length.
    Returns:
        None.
    Raises:
        AssertionError: If truncation markers are missing.
    """
    long_value = "a" * 200
    result = InspectorUtility.safe_repr(long_value, max_len=40)

    assert "len" in result
    assert "..." in result


def test_safe_repr_handles_repr_errors() -> None:
    """
    Purpose:
        Ensure safe_repr handles repr failures.
    Contract:
        Returns a placeholder containing the type name.
    Returns:
        None.
    Raises:
        AssertionError: If fallback formatting is incorrect.
    """
    result = InspectorUtility.safe_repr(_ReprBoom(), max_len=50)
    assert "unrepr-able" in result
    assert "_ReprBoom" in result


def test_unwrap_callable_follows_closure_wrapped_function() -> None:
    """
    Purpose:
        Verify unwrap_callable discovers closure-captured originals.
    Contract:
        Returns the original function when wrapped without functools.wraps.
    Returns:
        None.
    Raises:
        AssertionError: If unwrapping fails to recover the original.
    """
    wrapped = _simple_decorator(_original_function)
    unwrapped = InspectorUtility.unwrap_callable(wrapped)
    assert unwrapped is _original_function


def test_method_inspector_prefers_unwrapped_signature() -> None:
    """
    Purpose:
        Confirm MethodInspector reports the unwrapped signature.
    Contract:
        The inspected signature reflects the original callable.
    Returns:
        None.
    Raises:
        AssertionError: If signature or decoration flags are incorrect.
    """
    wrapped = _simple_decorator(_original_function)
    data = MethodInspector(wrapped).inspect()

    assert data["name"] == "_original_function"
    assert "other=1" in data["signature"]
    assert data["decorated"] is True
