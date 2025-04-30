import threading
from typing import Optional, Type
from melder.utilities.concurrent_dictionary import ConcurrentDict
from melder.utilities.interfaces import ISeal

class SpellFrame(ISeal):
    """
    Singleton registry for managing and validating unique SpellFrame interfaces.

    Each SpellFrame is:
        - A Python class (typically an abstract interface or base contract)
        - Registered exactly once (identified by its memory id)
        - Rejected if marked as disabled via the `__spell_disabled__` attribute
        - Validated at runtime via isinstance checks

    This registry supports:
        - Safe runtime enforcement of frame compliance
        - Internal metadata tracking for debugging or export
        - Optional sealing to lock the registry and clear its contents
    """

    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SpellFrame, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not SpellFrame._initialized:
            self._sealed = False
            super().__init__()
            self._frame_map = ConcurrentDict()  # {id(frame_type): metadata}
            SpellFrame._initialized = True

    def bind(self, frame_type: Type):
        """
        Registers a SpellFrame type into the registry.

        Args:
            frame_type (Type): The class/interface to register.

        Raises:
            TypeError: If frame_type is not a class.
            ValueError: If already registered or marked as disabled.
        """
        if self._sealed:
            raise RuntimeError("SpellFrame registry is sealed and cannot be modified.")

        if not isinstance(frame_type, type):
            raise TypeError("Only class types can be registered as SpellFrames.")

        frame_id = id(frame_type)

        if frame_id in self._frame_map:
            raise ValueError(f"SpellFrame '{frame_type.__name__}' is already registered.")

        if getattr(frame_type, "__spell_disabled__", False):
            raise ValueError(f"SpellFrame '{frame_type.__name__}' is disabled and cannot be registered.")

        self._frame_map[frame_id] = {
            "frame": frame_type,
            "name": frame_type.__name__,
            "module": frame_type.__module__,
            "qualname": frame_type.__qualname__,
            "id": frame_id,
        }

    def validate(self, obj, frame_type: Type) -> bool:
        """
        Verifies that an object conforms to a registered SpellFrame.

        Args:
            obj: The object to check.
            frame_type (Type): The SpellFrame class the object must implement.

        Returns:
            bool: True if compliant.

        Raises:
            ValueError: If the frame_type is not registered.
            TypeError: If the object does not conform.
        """
        frame_id = id(frame_type)

        if frame_id not in self._frame_map:
            raise ValueError(f"SpellFrame '{frame_type.__name__}' has not been registered.")

        if not isinstance(obj, frame_type):
            raise TypeError(f"Object does not comply with SpellFrame '{frame_type.__name__}'.")

        return True

    def meld(self, frame_type: Type) -> Optional[dict]:
        """
        Retrieves metadata for a registered SpellFrame.

        Args:
            frame_type (Type): The SpellFrame class to query.

        Returns:
            Optional[dict]: Metadata dict, or None if not found.
        """
        return self._frame_map.get(id(frame_type))

    def _reset_for_testing(self):
        with self._lock:
            self._frame_map.clear()
            self._sealed = False
            SpellFrame._initialized = False
            SpellFrame._instance = None

    def seal(self):
        """
        Seals the SpellFrame registry. This:
            - Clears all registered frames
            - Prevents any further registration attempts
        """
        with self._lock:
            if self._sealed:
                return
            self._frame_map.clear()
            self._sealed = True
