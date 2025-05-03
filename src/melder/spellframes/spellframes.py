import threading
import uuid
from typing import Optional, Type, Dict, Any
from melder.utilities.concurrent_dictionary import ConcurrentDict
from melder.utilities.interfaces import ISeal


class SpellFrame(ISeal):
    """
    SpellFrame: A singleton interface registry for AI-generated or dynamically composed class interfaces.

    ⚠️ Not intended for traditional, static interface development.

    SpellFrame is a runtime-only registry used to bind, track, and validate AI-generated or
    dynamically resolved interface classes. It supports storing metadata like UUIDs, method/property maps,
    and module information, enabling runtime introspection, dependency injection, or agentic behavior modeling.

    Common use cases:
        - AI-generated service contracts
        - Runtime-defined plugin schemas
        - Dynamic behavior trees or agent frameworks
        - Code synthesis systems that evolve structure during runtime

    Design Rationale:
        - Not compatible with static typing tools or linters (e.g., Pyright, MyPy)
        - Designed for frameworks where class structures are generated or mutated at runtime
        - Enables systems to reason about available capabilities, even if the code is fluid
        - Avoids traditional interface inheritance patterns, and instead tracks class structure reflectively

    Features:
        - Uses the class `__name__` as a unique key
        - Prevents duplicate bindings
        - Generates and stores UUIDs for each frame
        - Inspects and tracks public methods and properties
        - Supports metadata injection for downstream introspection or serialization
        - Can be sealed to disable further registrations (for safety or immutability)

    ⚠️ Developers working on typical business applications, libraries, or team-based codebases should NOT
       rely on SpellFrame for interface management. Prefer static interfaces, `abc.ABC`, or formal DI frameworks instead.

    SpellFrame is built for the future — for AI-native runtimes that change and grow.
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
