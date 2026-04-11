from functools import update_wrapper
from typing import Type, Callable, Optional, Any


def class_wraps(decorator_name: Optional[str] = None):
    """
    Return a :func:`functools.wraps`-style helper for class decorators.

    Purpose:
        Make class decorators preserve inspection metadata on the class they
        return, not just on the decorator function itself.

    Contract:
        - Stamps the produced class with `__wrapped__` and `__is_wrapped__`.
        - Optionally stamps `__decorator_name__` for later inspection.
        - Preserves the original decorator function metadata on the wrapper via
          `update_wrapper(...)`.

    Args:
        decorator_name (Optional[str]): Optional inspection label stored on the
            decorated class as ``__decorator_name__``.

    Returns:
        Callable[[Callable[[Type], Type]], Callable[[Type], Type]]: Decorator
        factory that stamps the produced class with ``__wrapped__`` and
        ``__is_wrapped__`` metadata while preserving the original decorator's
        function metadata.

    Usage:

        @class_wraps("my_decorator")
        def my_decorator(cls: type) -> type:
            class Wrapped(cls):
                ...
            return Wrapped

    Behavior:
        - Attaches ``__wrapped__`` on the *returned class* pointing to the
          original class.
        - Sets ``__is_wrapped__ = True``.
        - Optionally sets ``__decorator_name__`` for inspection.
    """
    def decorator_wrapper(deco: Callable[[Type], Type]) -> Callable[[Type], Type]:
        """
        Wrap one class decorator so the produced class exposes inspection metadata.
        """

        def wrapped(cls: Type) -> Type:
            """
            Apply the decorator and stamp the returned class with wrapper metadata.
            """
            new_cls = deco(cls)
            # Stamp the produced class, not the input class, so runtime
            # inspection sees the type that callers will actually instantiate.
            setattr(new_cls, "__wrapped__", cls)
            setattr(new_cls, "__is_wrapped__", True)
            if decorator_name is not None:
                setattr(new_cls, "__decorator_name__", decorator_name)
            return new_cls

        # Preserve the original decorator function metadata on the wrapper so
        # introspection still reports the real decorator entrypoint.
        return update_wrapper(wrapped, deco)

    return decorator_wrapper
