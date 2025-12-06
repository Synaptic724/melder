from functools import update_wrapper
from typing import Type, Callable, Optional, Any


def class_wraps(decorator_name: Optional[str] = None):
    """
    Class-friendly analogue of :func:`functools.wraps` for **class decorators**.

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
        def wrapped(cls: Type) -> Type:
            new_cls = deco(cls)
            # new_cls is the actual decorated class we will instantiate
            setattr(new_cls, "__wrapped__", cls)
            setattr(new_cls, "__is_wrapped__", True)
            if decorator_name is not None:
                setattr(new_cls, "__decorator_name__", decorator_name)
            return new_cls

        # Copy metadata from the original decorator function to the wrapper.
        return update_wrapper(wrapped, deco)

    return decorator_wrapper
