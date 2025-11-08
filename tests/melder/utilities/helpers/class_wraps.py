

from functools import update_wrapper
from typing import Type, Callable

# This module provides a decorator for wrapping classes, similar to functools.wraps,
# but specifically designed for class decorators. It allows you to add metadata
# to the wrapped class, such as __wrapped__, __decorator_name__, and __is_wrapped__.

def class_wraps(original_cls: Type, decorator_name: str = None):
    """
    Class-friendly version of functools.wraps that enables decorator tracking and inspection.

    Adds:
    - __wrapped__: link to the original class
    - __decorator_name__: optional label
    - __is_wrapped__: always True
    """
    def wrapper(decorator: Callable) -> Callable:
        def wrapped_class(*args, **kwargs):
            return decorator(*args, **kwargs)
        # Attach metadata to the decorator function
        update_wrapper(wrapped_class, decorator)
        setattr(wrapped_class, "__wrapped__", original_cls)
        setattr(wrapped_class, "__is_wrapped__", True)
        if decorator_name:
            setattr(wrapped_class, "__decorator_name__", decorator_name)
        return wrapped_class
    return wrapper
