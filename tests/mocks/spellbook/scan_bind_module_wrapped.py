"""
Decorator stacking mock module for scan_bind integration tests.

Defines decorated functions with varying decorator orders to validate metadata
preservation via functools.wraps vs bare wrappers.
"""
from functools import wraps
from typing import Any

from melder.spellbook.bind.scan import scan_bind
from melder.spellbook.existence.existence import Existence


def _simple_wrap(func: Any) -> Any:
    """
    Purpose:
        Provide a decorator that wraps without preserving __dict__.
    Contract:
        Returns a wrapper that forwards all arguments to the wrapped function.
    Args:
        func: Callable being wrapped.
    Returns:
        Any: Wrapper callable.
    """
    def wrapper(*args, **kwargs):
        """
        Purpose:
            Forward calls to the wrapped function.
        Contract:
            Returns the wrapped function result.
        Args:
            *args: Positional arguments for the wrapped function.
            **kwargs: Keyword arguments for the wrapped function.
        Returns:
            Any: Result from the wrapped function.
        """
        return func(*args, **kwargs)
    return wrapper


def _wraps_wrap(func: Any) -> Any:
    """
    Purpose:
        Provide a decorator that preserves metadata via functools.wraps.
    Contract:
        Returns a wrapper with __dict__ updated from the wrapped function.
    Args:
        func: Callable being wrapped.
    Returns:
        Any: Wrapper callable with copied metadata.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        Purpose:
            Forward calls to the wrapped function.
        Contract:
            Returns the wrapped function result.
        Args:
            *args: Positional arguments for the wrapped function.
            **kwargs: Keyword arguments for the wrapped function.
        Returns:
            Any: Result from the wrapped function.
        """
        return func(*args, **kwargs)
    return wrapper


@scan_bind(
    existence=Existence.unique,
    permissions="create",
    spellframe="scan_wrapped",
    binding_name="outer_no_wrap",
)
@_simple_wrap
def scan_outer_no_wrap() -> str:
    """
    Purpose:
        Decorated function with scan_bind outermost and bare wrapper inner.
    Contract:
        Returns a stable string value.
    Returns:
        str: Stable marker value.
    """
    return "outer_no_wrap"


@_simple_wrap
@scan_bind(
    existence=Existence.unique,
    permissions="create",
    spellframe="scan_wrapped",
    binding_name="inner_no_wrap",
)
def scan_inner_no_wrap() -> str:
    """
    Purpose:
        Decorated function with scan_bind inner and bare wrapper outer.
    Contract:
        Returns a stable string value.
    Returns:
        str: Stable marker value.
    """
    return "inner_no_wrap"


@_wraps_wrap
@scan_bind(
    existence=Existence.unique,
    permissions="create",
    spellframe="scan_wrapped",
    binding_name="inner_wraps",
)
def scan_inner_wraps() -> str:
    """
    Purpose:
        Decorated function with scan_bind inner and wraps-based wrapper outer.
    Contract:
        Returns a stable string value.
    Returns:
        str: Stable marker value.
    """
    return "inner_wraps"
