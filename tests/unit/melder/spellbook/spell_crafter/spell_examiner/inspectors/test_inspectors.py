from functools import wraps
import inspect
from types import SimpleNamespace

from melder.aether.spellbook.spell_crafter.spell_examiner.inspectors.inspector_utility import (
    InspectorUtility,
)
from melder.aether.spellbook.spell_crafter.spell_examiner.inspectors.method_inspector import (
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


def _wraps_decorator(fn):
    """
    Purpose:
        Create a wrapper that preserves __wrapped__ using functools.wraps.
    Contract:
        Returns a callable that forwards calls to the wrapped function.
    Args:
        fn: Callable to wrap.
    Returns:
        callable: Wrapper that forwards all arguments.
    """
    @wraps(fn)
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


class _MethodContainer:
    """
    Purpose:
        Provide classmethod/staticmethod targets for MethodInspector tests.
    Contract:
        Exposes a classmethod and staticmethod with stable signatures.
    """
    @classmethod
    def make(cls, value: int) -> int:
        """
        Purpose:
            Provide a classmethod for inspection.
        Contract:
            Returns the input value.
        Args:
            value: Input value.
        Returns:
            int: The same value passed in.
        """
        return value

    @staticmethod
    def ping(value: int) -> int:
        """
        Purpose:
            Provide a staticmethod for inspection.
        Contract:
            Returns the input value.
        Args:
            value: Input value.
        Returns:
            int: The same value passed in.
        """
        return value


def _make_closure():
    """
    Purpose:
        Build a callable with a captured closure for inspector tests.
    Contract:
        Returns a function that captures a local variable.
    Returns:
        callable: Closure-based function.
    """
    captured = {"key": "value"}

    def _inner(value: str) -> str:
        """
        Purpose:
            Provide a closure-based callable for inspection.
        Contract:
            Returns the captured value concatenated with input.
        Args:
            value: Input value to append.
        Returns:
            str: Combined string.
        """
        return f"{captured['key']}-{value}"

    return _inner


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


def test_safe_repr_returns_full_repr_when_short() -> None:
    """
    Purpose:
        Confirm safe_repr leaves short representations unchanged.
    Contract:
        The output equals repr(obj) when below max_len.
    Returns:
        None.
    Raises:
        AssertionError: If the repr is unexpectedly truncated.
    """
    value = {"a": 1}
    result = InspectorUtility.safe_repr(value, max_len=50)
    assert result == repr(value)


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


def test_is_extension_module_detects_spec_origin() -> None:
    """
    Purpose:
        Validate extension-module detection via __spec__.origin.
    Contract:
        Origins ending in extension suffixes return True; others return False.
    Returns:
        None.
    Raises:
        AssertionError: If detection does not match the origin suffix.
    """
    ext_module = SimpleNamespace(__spec__=SimpleNamespace(origin="x.pyd"))
    non_ext_module = SimpleNamespace(__spec__=SimpleNamespace(origin="x.py"))

    assert InspectorUtility.is_extension_module(ext_module) is True
    assert InspectorUtility.is_extension_module(non_ext_module) is False


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


def test_unwrap_callable_uses_wrapped_attribute() -> None:
    """
    Purpose:
        Ensure unwrap_callable follows functools.wraps metadata.
    Contract:
        Returns the original function when __wrapped__ is present.
    Returns:
        None.
    Raises:
        AssertionError: If unwrap_callable does not follow __wrapped__.
    """
    wrapped = _wraps_decorator(_original_function)
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
    assert data["signature"] == str(inspect.signature(_original_function))
    assert data["decorated"] is True


def test_method_inspector_detects_classmethod_and_staticmethod() -> None:
    """
    Purpose:
        Verify MethodInspector flags classmethod and staticmethod traits.
    Contract:
        classmethod=True for class methods and staticmethod=True for static methods.
    Returns:
        None.
    Raises:
        AssertionError: If trait detection is incorrect.
    """
    class_data = MethodInspector(_MethodContainer.make).inspect()
    static_data = MethodInspector(_MethodContainer.ping).inspect()

    assert class_data["classmethod"] is True
    assert class_data["staticmethod"] is False
    assert static_data["staticmethod"] is True
    assert static_data["classmethod"] is False


def test_method_inspector_captures_closure_preview() -> None:
    """
    Purpose:
        Ensure MethodInspector captures closure previews when present.
    Contract:
        The closure list is populated with safe representations.
    Returns:
        None.
    Raises:
        AssertionError: If closure data is missing or empty.
    """
    closure_fn = _make_closure()
    data = MethodInspector(closure_fn).inspect()

    assert isinstance(data.get("closure"), list)
    assert data["closure"]
