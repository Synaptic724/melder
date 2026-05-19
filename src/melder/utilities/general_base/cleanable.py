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

    class _CleanupContext:
        """
        Standalone context manager that guarantees one cleanup call on exit.

        Contract:
            - Does not rely on the owner's own `__enter__` / `__exit__`.
            - Calls `owner.cleanup()` at most once.
            - Drops the strong owner reference after exit.
            - Never suppresses exceptions raised by the caller's block.
        """
        __slots__ = ("_owner", "_cleaned", "_lock")

        _cleaned: bool

        def __init__(self, owner: "Cleanable") -> None:
            """
            Bind the helper context to one cleanable owner.

            Contract:
            - Stores one strong owner reference until exit.
            - Tracks whether cleanup has already been triggered so exit remains
              idempotent.
            """
            self._owner: Optional["Cleanable"] = owner
            self._cleaned: bool = False
            self._lock: threading.RLock = threading.RLock()

        def __enter__(self) -> "Cleanable":
            """
            Enter the cleanup helper context and return the owner.

            Returns:
                Cleanable:
                    The owner object protected by this helper.
            """
            self._lock.acquire()
            if self._owner is None:
                raise RuntimeError("Cleanup context no longer owns a live object.")
            return self._owner

        def __exit__(
                self,
                exc_type: Optional[Type[BaseException]],
                exc: Optional[BaseException],
                tb: Optional[TracebackType],
        ) -> Literal[False]:
            """
            Exit the cleanup helper context and trigger owner cleanup once.

            Returns:
                Literal[False]:
                    Always False so caller exceptions are never suppressed.
            """
            # Guarantee cleanup only once.
            try:
                owner = self._owner
                if owner is not None and not self._cleaned:
                    self._cleaned = True
                    try:
                        owner.cleanup()
                    except Exception:
                        pass

                # Explicitly drop the reference so nothing is leaked.
                self._owner = None

                # Do NOT suppress user exceptions.
                return False
            finally:
                self._lock.release()


    def using_cleanup(self) -> "_CleanupContext":
        """
        Return a helper context manager that guarantees `cleanup()` on exit.

        Contract:
        - Independent of any context-manager behavior implemented by the owner.
        - Intended for callers that want deterministic cleanup without relying
          on the object's own `__enter__` / `__exit__`.

        Returns:
            Cleanable._CleanupContext:
                Helper context manager bound to this object.
        """
        return Cleanable._CleanupContext(self)
