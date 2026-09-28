from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Concatenate, Generator, ParamSpec, TypeVar


P = ParamSpec("P")
R = TypeVar("R")
ViewMethod = Callable[Concatenate[Any, P], R]


def decorate_public_view_actions(cls: type) -> type:
    """
    Wrap public viewer methods in the shared view-action hook boundary.

    Contract:
        - Wraps only public callable methods.
        - Skips private helpers, properties, and cleanup.
        - Preserves method names and docstrings through `functools.wraps`.
    """
    for name, value in list(vars(cls).items()):
        if name.startswith("_") or name == "cleanup":
            continue
        if isinstance(value, property):
            continue
        if not callable(value):
            continue
        if getattr(value, "__view_action_wrapped__", False):
            continue
        setattr(cls, name, _wrap_view_action(name, value))
    return cls


def _wrap_view_action(
        action_name: str,
        method: ViewMethod[P, R],
) -> ViewMethod[P, R]:
    """
    Wrap one viewer method in the shared view-action hook boundary.

    Args:
        action_name:
            Stable viewer action name.
        method:
            Unwrapped viewer method.

    Returns:
        ViewMethod: Wrapped viewer method.
    """

    @wraps(method)
    def _wrapped(self: Any, *args: P.args, **kwargs: P.kwargs) -> R:
        with self._entered_view_action(action_name=action_name):
            return method(self, *args, **kwargs)

    setattr(_wrapped, "__view_action_wrapped__", True)
    return _wrapped


@contextmanager
def noop_action_scope() -> Generator[None, None, None]:
    """
    Return a no-op action scope when no viewer hook owner is available.

    Yields:
        None: No-op context manager payload.
    """
    yield
