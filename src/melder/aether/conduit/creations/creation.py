import threading
import ulid
from typing import Any
# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class Creation(Cleanable):
    """
    A wrapper around any instantiated object managed by Melder.

    Responsibilities:
    - Provide a unique ULID identity.
    - Encapsulate the underlying Python object.
    - Allow Creations/LesserCreations to manage disposal.
    - Store disposal metadata derived from the originating spell.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = (
        "_id",
        "_value",
        "_cleaned",
        "_has_disposal_methods",
        "_disposal_methods",
        "_lock",
    )

    def __init__(
            self,
            value: Any,
            *,
            has_disposal_methods: bool = False,
            disposal_methods: list[str] | None = None,
    ):
        """
        Wrap an object into a Creation container.

        Args:
            value: Any Python object produced by a Spell.
            has_disposal_methods: True when the spell declares disposal methods.
            disposal_methods: Ordered list of disposal method names for this creation.
        """
        super().__init__()
        self._id: str = str(ulid.ULID())
        self._lock : threading.RLock = threading.RLock()
        self._has_disposal_methods: bool = bool(has_disposal_methods)
        self._disposal_methods: list[str] = list(disposal_methods) if disposal_methods else []
        self._value: Any = value

    def cleanup(self):
        """
        Cleanup the wrapper.

        IMPORTANT:
        - Does NOT call cleanup()/close()/dispose() on the underlying object.
        - Creations and LesserCreations are responsible for disposing the inner value.
        - This method ONLY nulls out the internal reference so GC can eventually reclaim it.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._value = None   # Underlying object is not disposed here.
            self._has_disposal_methods = None
            self._disposal_methods = None
        self._lock = None

    @property
    def id(self) -> str:
        """Return the ULID identity for this creation."""
        return self._id

    @property
    def value(self) -> Any:
        """Return the underlying Python object wrapped by this Creation."""
        return self._value

    def __repr__(self) -> str:
        return f"<Creation id={self._id} value={self._value!r}>"

    def __enter__(self) -> 'Creation':
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._lock.release()
