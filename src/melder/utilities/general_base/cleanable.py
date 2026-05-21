import threading
from abc import ABC, abstractmethod
from types import TracebackType
from typing import Literal, Optional, Type

from mypy_extensions import mypyc_attr


@mypyc_attr(native_class=True)
class Cleanable(ABC):
    """
    Abstract base class for objects that own explicit cleanup lifecycle.

    `Cleanable` is the common contract used across the runtime for objects that
    own resources, registration state, or other teardown-sensitive runtime
    surfaces. Subclasses are responsible for implementing deterministic cleanup
    behavior and for exposing the cleaned-state guard consistently.

    Contract:
    - `cleanup()` must be idempotent.
    - Subclasses must set `_cleaned = True` when cleanup completes.
    - `check_cleaned()` is the canonical guard for rejecting use-after-clean.
    - `using_cleanup()` provides a separate helper context that guarantees one
      cleanup call on exit.
    """

    __slots__ = ['_cleaned']

    _cleaned: bool

    def __init__(self) -> None:
        """
        Initialize the live/cleaned lifecycle flag for a new cleanable object.

        Contract:
        - Every `Cleanable` starts live with `_cleaned=False`.
        - Subclasses may extend initialization, but they inherit this one
          canonical cleaned-state flag.
        """
        self._cleaned: bool = False

    @property
    def cleaned(self) -> bool:
        """
        Return whether the object has already been cleaned.

        Returns:
            bool:
                True when `_cleaned` has been set.
        """
        return self._cleaned

    @property
    def is_cleaned(self) -> bool:
        """
        Alias for `cleaned`.

        Returns:
            bool:
                Current cleaned-state flag.
        """
        return self._cleaned

    def check_cleaned(self) -> None:
        """
        Raise when the object has already been cleaned.

        Contract:
        - Subclasses use this as the standard use-after-clean guard.
        - No-op while the object is still live.

        Raises:
            RuntimeError: If the object has already been cleaned.
        """
        if self._cleaned:
            raise RuntimeError(f"{self.__class__.__name__} has already been cleaned. ")

    @abstractmethod
    def cleanup(self) -> None:
        """
        Release owned resources and mark the object cleaned.

        Subclass contract:
        - Release all resources.
        - Deregister or finalize any allocations.
        - Be idempotent (safe to call multiple times).
        """
        raise NotImplementedError("Subclasses must implement cleanup().")

    async def async_cleanup(self) -> None:
        """
        Async cleanup hook for subclasses that support asynchronous teardown.

        Subclass contract:
        - Release all resources.
        - Deregister or finalize any allocations.
        - Be idempotent (safe to call multiple times).
        - Preserve the same lifecycle semantics as `cleanup()` once async
          teardown completes.
        """
        raise NotImplementedError("Subclasses must implement async_cleanup().")