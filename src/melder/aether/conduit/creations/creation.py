import threading
import ulid
from types import TracebackType
from typing import Any, ClassVar



# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg



class Creation(Cleanable):
    """
    Wrapper for one live runtime object tracked by `Creations`.

    `Creation` is the small ownership shell around an instantiated object. It
    gives the runtime a stable identity, stores disposal metadata derived from
    the originating spell, and lets the larger `Creations` manager handle
    registration, extraction, restoration, and ordered disposal.

    Contract:
    - The wrapper owns metadata about disposal, not disposal policy itself.
    - `cleanup()` clears the wrapper's references but does not call
      `cleanup()` / `close()` / `dispose()` on the wrapped object.
    - The actual disposal decision belongs to `Creations`.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_value",
        "_has_disposal_methods",
        "_disposal_methods",
        "_lock",
    ]

    def __init__(
            self,
            value: Any,
            *,
            has_disposal_methods: bool = False,
            disposal_methods: list[str] | None = None,
    ):
        """
        Wrap one runtime object in a `Creation` shell.

        Args:
            value: Runtime object produced by a spell.
            has_disposal_methods: Whether the originating spell declared
                disposal methods for the wrapped object.
            disposal_methods: Ordered disposal-method names to be interpreted
                later by `Creations`.
        """
        super().__init__()
        self._id: str = str(ulid.ULID())
        self._lock : threading.RLock = threading.RLock()
        self._has_disposal_methods: bool = bool(has_disposal_methods)
        self._disposal_methods: list[str] = list(disposal_methods) if disposal_methods else []
        self._value: Any = value

    def cleanup(self) -> None:
        """
        Release the wrapper's references without disposing of the wrapped object.

        Contract:
        - Idempotent and lock-protected.
        - Does not call disposal methods on the underlying value.
        - Only clears wrapper-held references so the higher-level `Creations`
          manager can own the actual disposal policy.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            del self._value   # Underlying object is not disposed here.
            del self._has_disposal_methods
            del self._disposal_methods
        del self._lock

    @property
    def id(self) -> str:
        """
        Return the stable ULID assigned to this wrapper.
        """
        self.check_cleaned()
        return self._id

    @property
    def value(self) -> Any:
        """
        Return the wrapped runtime object.
        """
        self.check_cleaned()
        return self._value

    @property
    def has_disposal_methods(self) -> bool | None:
        """
        Return whether the originating spell declared disposal methods.

        Contract:
            - True/False while the Creation is active.
            - None after cleanup.
        """
        self.check_cleaned()
        return self._has_disposal_methods

    @property
    def disposal_method_names(self) -> list[str] | None:
        """
        Return the ordered disposal method names recorded for this Creation.

        Contract:
            - List of method names while the Creation is active.
            - None after cleanup.
        """
        self.check_cleaned()
        return self._disposal_methods

    def __repr__(self) -> str:
        """
        Return a debug-oriented representation of the wrapper.
        """
        self.check_cleaned()
        return f"<Creation id={self._id} value={self._value!r}>"

    def __enter__(self) -> 'Creation':
        """
        Enter the wrapper lock context.

        Returns:
            Creation: The wrapper itself while its internal lock is held.
        """
        self.check_cleaned()
        self._lock.acquire()
        return self

    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_value: BaseException | None,
            traceback: TracebackType | None,
    ) -> None:
        """
        Exit the wrapper lock context.

        Args:
            exc_type: Exception type raised inside the context, if any.
            exc_value: Exception instance raised inside the context.
            traceback: Traceback for the exception, if any.
        """
        self._lock.release()
