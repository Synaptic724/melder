import threading
import uuid
from typing import Optional, Type, Dict, Any
from melder.utilities.concurrent_dictionary import ConcurrentDict
from melder.utilities.interfaces import ISeal


class SpellFrame(ISeal):
    """
    Singleton registry for managing and validating unique SpellFrame interfaces.

    Enhancements:
        - Uses class name as key instead of memory id
        - Assigns UUID to each registered frame
        - Allows custom metadata injection
        - Inspects class structure for debugging or auditing
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
            self._frame_map: ConcurrentDict[str, Dict[str, Any]] = ConcurrentDict()
            SpellFrame._initialized = True

    def bind(self, frame_type: Type, extra_metadata: Optional[Dict[str, Any]] = None):
        """
        Registers a SpellFrame class.

        Args:
            frame_type (Type): Class to register.
            extra_metadata (dict, optional): Additional metadata to attach.

        Raises:
            TypeError: If frame_type is not a class.
            ValueError: If already registered or disabled.
        """
        if self._sealed:
            raise RuntimeError("SpellFrame registry is sealed and cannot be modified.")

        if not isinstance(frame_type, type):
            raise TypeError("Only class types can be registered as SpellFrames.")

        if getattr(frame_type, "__spell_disabled__", False):
            raise ValueError(f"SpellFrame '{frame_type.__name__}' is disabled.")

        name = frame_type.__name__
        if name in self._frame_map:
            raise ValueError(f"SpellFrame '{name}' is already registered.")

        metadata = {
            "uuid": str(uuid.uuid4()),
            "name": name,
            "module": frame_type.__module__,
            "qualname": frame_type.__qualname__,
            "methods": [m for m in dir(frame_type) if callable(getattr(frame_type, m)) and not m.startswith("__")],
            "properties": [a for a in dir(frame_type) if not callable(getattr(frame_type, a)) and not a.startswith("__")],
            "type": frame_type,
        }

        if extra_metadata:
            metadata.update(extra_metadata)

        self._frame_map[name] = metadata

    def validate(self, obj: Any, frame_type: Type) -> bool:
        """
        Validates that `obj` is an instance of a registered frame_type.

        Raises:
            ValueError: If the frame_type is not registered.
            TypeError: If the object is not a valid instance.
        """
        name = frame_type.__name__

        if name not in self._frame_map:
            raise ValueError(f"SpellFrame '{name}' is not registered.")

        if not isinstance(obj, frame_type):
            raise TypeError(f"Object does not conform to SpellFrame '{name}'.")

        return True

    def meld(self, frame_type: Type) -> Optional[Dict[str, Any]]:
        """
        Retrieves metadata for a registered SpellFrame.

        Returns:
            Metadata dict or None if not found.
        """
        return self._frame_map.get(frame_type.__name__)

    def _reset_for_testing(self):
        with self._lock:
            self._frame_map.clear()
            self._sealed = False
            SpellFrame._initialized = False
            SpellFrame._instance = None

    def seal(self):
        """
        Seals the registry and clears all entries.
        """
        with self._lock:
            if self._sealed:
                return
            self._frame_map.clear()
            self._sealed = True
